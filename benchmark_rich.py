#!/usr/bin/env python3

import json
import os
import re
import subprocess
import time
from pathlib import Path

SKYLOS_CONFIDENCE = 20

EXPECTED_UNUSED = {
    "functions": [
        ("rich/console.py", "_svg_hash"),
    ],
    "variables": [
        ("rich/tree.py", "GuideType"),
        ("rich/_export_format.py", "_SVG_FONT_FAMILY"),
        ("rich/_export_format.py", "_SVG_CLASSES_PREFIX"),
        ("rich/logging.py", "foos"),
        ("rich/box.py", "SIMPLE_HEAD"),
        ("rich/box.py", "HORIZONTALS"),
        ("rich/box.py", "DOUBLE_EDGE"),
        ("rich/box.py", "MARKDOWN"),
        ("rich/terminal_theme.py", "DIMMED_MONOKAI"),
        ("rich/terminal_theme.py", "NIGHT_OWLISH"),
    ],
    "imports": [],
    "classes": [
        ("rich/markdown.py", "HeadingFormat"),
        ("rich/errors.py", "StyleStackError"),
    ],
}

ACTUALLY_USED = [
    ("rich/logging.py", "emit"),
    ("rich/logging.py", "render_message"),
    ("rich/jupyter.py", "_repr_mimebundle_"),
    ("rich/errors.py", "LiveError"),
    ("rich/prompt.py", "FloatPrompt"),
    ("rich/console.py", "get_windows_console_features"),
    ("rich/table.py", "box"),
    ("rich/console.py", "_term_name"),
    ("rich/console.py", "_hyphen"),
    ("rich/color.py", "_h"),
    ("rich/layout.py", "_x"),
    ("rich/layout.py", "_layout_width"),
    ("rich/columns.py", "_top"),
    ("rich/columns.py", "_bottom"),
    ("rich/_inspect.py", "_error"),
    ("rich/syntax.py", "_token_type"),
    ("rich/syntax.py", "_pad_top"),
    ("rich/syntax.py", "_pad_bottom"),
    ("rich/ansi.py", "_params"),
    ("rich/traceback.py", "_rich_traceback_guard"),
    ("tests/test_traceback.py", "_rich_traceback_omit"),
    ("rich/traceback.py", "zed"),
    ("rich/scope.py", "list_of_things"),
    ("rich/scope.py", "dict_of_things"),
    ("rich/terminal_theme.py", "MONOKAI"),
    ("rich/syntax.py", "_pygments_style_class"),
    ("tests/test_pretty.py", "z"),
]


def get_all_expected():
    items = []
    for category, entries in EXPECTED_UNUSED.items():
        for file, name in entries:
            items.append((file, name, category))
    return items


def _parse_skylos_output(stdout):
    data = json.loads(stdout)
    findings = []
    for key, cat in [
        ("unused_functions", "functions"),
        ("unused_imports", "imports"),
        ("unused_variables", "variables"),
        ("unused_classes", "classes"),
    ]:
        for item in data.get(key, []):
            findings.append(
                (
                    item.get("file", ""),
                    item.get("simple_name", item.get("name", "")),
                    cat,
                )
            )

    cwd = os.getcwd()
    normalized = []
    for file, name, cat in findings:
        file = file.replace("\\", "/")
        if file.startswith(cwd):
            file = file[len(cwd) :].lstrip("/")
        elif file.startswith("/"):
            for prefix in ("rich/", "tests/"):
                marker = f"/{prefix}"
                if marker in file:
                    file = prefix + file.split(marker, 1)[1]
                    break
        if file.startswith("./"):
            file = file[2:]
        if "." in name and "/" not in name and not name.startswith("_"):
            name = name.split(".")[-1]
        normalized.append((file, name, cat))
    return normalized


def run_skylos(confidence=SKYLOS_CONFIDENCE):
    trace_file = Path.cwd() / ".skylos_trace"
    if trace_file.exists():
        trace_file.unlink()

    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            ["skylos", "rich/", "tests/", "--json", "--confidence", str(confidence)],
            capture_output=True,
            text=True,
        )
        duration = time.perf_counter() - start_time
        return _parse_skylos_output(result.stdout), duration
    except Exception as e:
        print(f"Skylos (static) error: {e}")
        return [], 0.0


def run_skylos_trace(confidence=SKYLOS_CONFIDENCE):
    trace_file = Path.cwd() / ".skylos_trace"
    if trace_file.exists():
        trace_file.unlink()

    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            ["skylos", "rich/", "tests/", "--json", "--trace", "--confidence", str(confidence)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        duration = time.perf_counter() - start_time
        findings = _parse_skylos_output(result.stdout)
        if trace_file.exists():
            trace_file.unlink()
        return findings, duration
    except subprocess.TimeoutExpired:
        print("Skylos (trace) timed out after 300s")
        return [], 0.0
    except Exception as e:
        print(f"Skylos (trace) error: {e}")
        return [], 0.0


def run_vulture():
    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            ["vulture", "rich/", "tests/", "--min-confidence", "20"],
            capture_output=True,
            text=True,
        )
        duration = time.perf_counter() - start_time
        findings = []
        pattern = r"(.+?):(\d+): unused (\w+) '(\w+)'"
        for line in result.stdout.splitlines():
            match = re.search(pattern, line)
            if match:
                file = match.group(1).replace("\\", "/")
                if file.startswith("./"):
                    file = file[2:]
                kind = match.group(3)
                name = match.group(4)
                cat_map = {
                    "function": "functions",
                    "variable": "variables",
                    "import": "imports",
                    "class": "classes",
                    "attribute": "variables",
                    "method": "functions",
                    "property": "functions",
                }
                cat = cat_map.get(kind, kind)
                findings.append((file, name, cat))
        return findings, duration
    except Exception as e:
        print(f"Vulture error: {e}")
        return [], 0.0


def _calc_metrics(tool_set, expected_set, used_set):
    tp = tool_set & expected_set
    fp = tool_set & used_set
    fn = expected_set - tool_set
    total = len(expected_set)
    precision = len(tp) / (len(tp) + len(fp)) * 100 if (tp or fp) else 0
    recall = len(tp) / total * 100 if total else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0
    return len(tp), len(fp), len(fn), precision, recall, f1


def compare_results():
    expected = get_all_expected()
    expected_set = {(f, n) for f, n, _ in expected}
    used_set = {(f, n) for f, n in ACTUALLY_USED}

    print("Running Skylos (static)...")
    skylos_findings, skylos_time = run_skylos()
    skylos_set = {(f, n) for f, n, _ in skylos_findings}

    print("Running Skylos (trace) — this runs pytest, may take a minute...")
    trace_findings, trace_time = run_skylos_trace()
    trace_set = {(f, n) for f, n, _ in trace_findings}

    print("Running Vulture...")
    vulture_findings, vulture_time = run_vulture()
    vulture_set = {(f, n) for f, n, _ in vulture_findings}

    s_tp, s_fp, s_fn, s_prec, s_rec, s_f1 = _calc_metrics(skylos_set, expected_set, used_set)
    t_tp, t_fp, t_fn, t_prec, t_rec, t_f1 = _calc_metrics(trace_set, expected_set, used_set)
    v_tp, v_fp, v_fn, v_prec, v_rec, v_f1 = _calc_metrics(vulture_set, expected_set, used_set)

    print("\n" + "=" * 72)
    print("Benchmark: Skylos (Static) vs Skylos (Trace) vs Vulture")
    print("on Textualize/rich")
    print("=" * 72)
    print(f"\nRepository: Textualize/rich (~50,800 stars)")
    print(f"Ground truth: {len(expected_set)} dead items, {len(used_set)} confirmed-alive items\n")

    print("## Results\n")
    print("| Metric | Skylos Static | Skylos Trace | Vulture |")
    print("|--------|--------------|--------------|---------|")
    print(f"| True Positives (correctly found) | {s_tp} | {t_tp} | {v_tp} |")
    print(f"| False Positives (flagged but used) | {s_fp} | {t_fp} | {v_fp} |")
    print(f"| False Negatives (missed) | {s_fn} | {t_fn} | {v_fn} |")
    print(f"| Precision | {s_prec:.1f}% | {t_prec:.1f}% | {v_prec:.1f}% |")
    print(f"| Recall | {s_rec:.1f}% | {t_rec:.1f}% | {v_rec:.1f}% |")
    print(f"| F1 Score | {s_f1:.1f}% | {t_f1:.1f}% | {v_f1:.1f}% |")
    print(f"| Speed | {skylos_time:.2f}s | {trace_time:.2f}s | {vulture_time:.2f}s |")

    trace_eliminated = s_fp - t_fp
    if trace_eliminated > 0:
        print(f"\n→ Trace mode eliminated {trace_eliminated} additional false positives.")

    print("\n## Dead Code (should be found)\n")
    print("| Item | Category | Static | Trace | Vulture |")
    print("|------|----------|--------|-------|---------|")
    for file, name, cat in expected:
        s = "found" if (file, name) in skylos_set else "MISSED"
        t = "found" if (file, name) in trace_set else "MISSED"
        v = "found" if (file, name) in vulture_set else "MISSED"
        print(f"| `{file}:{name}` | {cat} | {s} | {t} | {v} |")

    print("\n## False Positives (flagged but actually used)\n")
    print("| Item | Why it's used | Static | Trace | Vulture |")
    print("|------|---------------|--------|-------|---------|")

    fp_reasons = {
        ("logging.py", "emit"): "logging.Handler protocol",
        ("logging.py", "render_message"): "Called by emit() line 167",
        ("jupyter.py", "_repr_mimebundle_"): "Jupyter display protocol",
        ("errors.py", "LiveError"): "Documented public API",
        ("prompt.py", "FloatPrompt"): "Documented public API",
        ("console.py", "get_windows_console_features"): "Used in detect_legacy_windows()",
        ("table.py", "box"): "Used throughout table.py",
        ("console.py", "_term_name"): "Tuple unpack discard",
        ("console.py", "_hyphen"): "Tuple unpack discard",
        ("color.py", "_h"): "Tuple unpack discard",
        ("layout.py", "_x"): "Tuple unpack discard",
        ("layout.py", "_layout_width"): "Tuple unpack discard",
        ("columns.py", "_top"): "Tuple unpack discard",
        ("columns.py", "_bottom"): "Tuple unpack discard",
        ("_inspect.py", "_error"): "Tuple unpack discard",
        ("syntax.py", "_token_type"): "Tuple unpack discard",
        ("syntax.py", "_pad_top"): "Tuple unpack discard",
        ("syntax.py", "_pad_bottom"): "Tuple unpack discard",
        ("ansi.py", "_params"): "Tuple unpack discard",
        ("traceback.py", "_rich_traceback_guard"): "Sentinel via f_locals.get()",
        ("test_traceback.py", "_rich_traceback_omit"): "Sentinel via f_locals.get()",
        ("traceback.py", "zed"): "Demo locals in traceback render",
        ("scope.py", "list_of_things"): "Used via locals() in render_scope",
        ("scope.py", "dict_of_things"): "Used via locals() in render_scope",
        ("terminal_theme.py", "MONOKAI"): "Documented public API theme",
        ("syntax.py", "_pygments_style_class"): "Type annotation, attr used",
        ("test_pretty.py", "z"): "Dataclass field in test",
    }

    any_fp = False
    for file, name in ACTUALLY_USED:
        s_flag = "FP" if (file, name) in skylos_set else "ok"
        t_flag = "FP" if (file, name) in trace_set else "ok"
        v_flag = "FP" if (file, name) in vulture_set else "ok"
        if s_flag != "ok" or t_flag != "ok" or v_flag != "ok":
            any_fp = True
            basename = file.split("/")[-1]
            reason = fp_reasons.get((basename, name), "Dynamic/protocol usage")
            print(f"| `{file}:{name}` | {reason} | {s_flag} | {t_flag} | {v_flag} |")

    if not any_fp:
        print("| (none) | | | | |")

    print("\n## Other Findings (not in ground truth)\n")
    all_known = expected_set | used_set
    skylos_other = skylos_set - all_known
    trace_other = trace_set - all_known
    vulture_other = vulture_set - all_known

    if skylos_other or trace_other or vulture_other:
        print("| Tool | File | Name |")
        print("|------|------|------|")
        for file, name in sorted(skylos_other):
            print(f"| Skylos Static | `{file}` | `{name}` |")
        for file, name in sorted(trace_other):
            if (file, name) not in skylos_other:
                print(f"| Skylos Trace | `{file}` | `{name}` |")
        for file, name in sorted(vulture_other):
            print(f"| Vulture | `{file}` | `{name}` |")
    else:
        print("(none)")


if __name__ == "__main__":
    compare_results()
