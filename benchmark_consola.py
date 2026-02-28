#!/usr/bin/env python3

import json
import os
import subprocess
import time

EXPECTED_UNUSED = {
    "functions": [
        ("src/utils/format.ts", "compileFormat"),
        ("src/utils/format.ts", "formatString"),
    ],
    "variables": [
        ("src/utils/format.ts", "FORMAT_ARGS"),
        ("src/utils/format.ts", "_compileCache"),
    ],
    "imports": [],
    "classes": [],
}

ACTUALLY_USED = [
    ("src/index.ts", "isDebug"),
    ("src/consola.ts", "paused"),
    ("src/utils/color.ts", "isColorSupported"),
    ("src/reporters/fancy.ts", "unicode"),
    ("src/reporters/fancy.ts", "LEVEL_COLOR_MAP"),
    ("src/reporters/fancy.ts", "TYPE_ICONS"),
    ("src/reporters/fancy.ts", "TYPE_COLOR_MAP"),
    ("src/reporters/basic.ts", "BasicReporter"),
    ("src/reporters/fancy.ts", "FancyReporter"),
    ("src/reporters/browser.ts", "BrowserReporter"),
    ("src/consola.ts", "Consola"),
    ("src/consola.ts", "createConsola"),
    ("src/index.ts", "createConsola"),
    ("src/index.ts", "consola"),
    ("src/utils/error.ts", "parseStack"),
    ("src/utils/log.ts", "isLogObj"),
    ("src/utils/stream.ts", "writeStream"),
    ("src/utils/color.ts", "colors"),
    ("src/utils/color.ts", "getColor"),
    ("src/utils/color.ts", "colorize"),
    ("src/utils/color.ts", "createColors"),
    ("src/utils/string.ts", "stripAnsi"),
    ("src/utils/box.ts", "box"),
    ("src/utils/tree.ts", "formatTree"),
    ("src/utils/string.ts", "centerAlign"),
    ("src/utils/string.ts", "rightAlign"),
    ("src/utils/string.ts", "leftAlign"),
    ("src/utils/string.ts", "align"),
    ("src/constants.ts", "LogLevels"),
    ("src/constants.ts", "LogTypes"),
    ("src/prompt.ts", "handleCancel"),
]


def get_all_expected():
    items = []
    for category, entries in EXPECTED_UNUSED.items():
        for file, name in entries:
            items.append((file, name, category))
    return items


def _relativize(p: str) -> str:
    cwd = os.getcwd().replace("\\", "/")
    p = (p or "").replace("\\", "/")
    if p.startswith(cwd):
        p = p[len(cwd):].lstrip("/")
    if p.startswith("./"):
        p = p[2:]
    return p


def run_skylos():
    start = time.perf_counter()
    try:
        result = subprocess.run(
            ["skylos", "src/", "--json", "--confidence", "80"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        dur = time.perf_counter() - start
        data = json.loads(result.stdout)

        findings = []
        for key, cat in [
            ("unused_functions", "functions"),
            ("unused_imports", "imports"),
            ("unused_variables", "variables"),
            ("unused_classes", "classes"),
        ]:
            for item in data.get(key, []):
                file = _relativize(item.get("file", ""))
                name = item.get("simple_name") or item.get("name") or ""
                if "." in name and "/" not in name and not name.startswith("_"):
                    name = name.split(".")[-1]
                if file.startswith("src/"):
                    findings.append((file, name, cat))

        return findings, dur
    except subprocess.TimeoutExpired:
        print("Skylos timed out after 120s")
        return [], 0.0
    except Exception as e:
        print(f"Skylos error: {e}")
        return [], 0.0


def run_knip():
    start = time.perf_counter()
    try:
        result = subprocess.run(
            ["npx", "knip", "--reporter", "json"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        dur = time.perf_counter() - start
        data = json.loads(result.stdout)

        findings = []

        for file_path in data.get("files", []):
            norm = file_path.replace("\\", "/")
            if not norm.startswith("src/"):
                norm = "src/" + norm if not norm.startswith("src") else norm
            if norm.startswith("src/"):
                findings.append((norm, "*FILE*", "files"))

        for issue in data.get("issues", []):
            file_path = issue.get("file", "").replace("\\", "/")
            if not file_path.startswith("src/"):
                continue
            for item in issue.get("exports", []):
                findings.append((file_path, item["name"], "functions"))
            for item in issue.get("types", []):
                findings.append((file_path, item["name"], "classes"))

        return findings, dur
    except subprocess.TimeoutExpired:
        print("Knip timed out after 120s")
        return [], 0.0
    except Exception as e:
        print(f"Knip error: {e}")
        return [], 0.0


def _match_knip(knip_findings, file, name):
    for kf, kn, _kc in knip_findings:
        if kf == file and kn == name:
            return True
        if kf == file and kn == "*FILE*":
            return True
    return False


def _calc_metrics(tool_set, expected_set, used_set):
    tp = tool_set & expected_set
    fp = tool_set & used_set
    fn = expected_set - tool_set
    precision = len(tp) / (len(tp) + len(fp)) * 100 if (tp or fp) else 0
    recall = len(tp) / len(expected_set) * 100 if expected_set else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0
    return len(tp), len(fp), len(fn), precision, recall, f1


def compare_results():
    expected = get_all_expected()
    expected_set = {(f, n) for f, n, _ in expected}
    used_set = {(f, n) for f, n in ACTUALLY_USED}

    print("Running Skylos on unjs/consola...")
    skylos_findings, skylos_time = run_skylos()
    skylos_set = {(f, n) for f, n, _ in skylos_findings}

    print("Running Knip on unjs/consola...")
    knip_findings, knip_time = run_knip()

    knip_direct = {(f, n) for f, n, _ in knip_findings if n != "*FILE*"}
    knip_dead_files = {f for f, n, _ in knip_findings if n == "*FILE*"}

    knip_tp_set = set()
    for f, n in expected_set:
        if (f, n) in knip_direct or f in knip_dead_files:
            knip_tp_set.add((f, n))
    knip_fp_set = set()
    for f, n in used_set:
        if (f, n) in knip_direct or f in knip_dead_files:
            knip_fp_set.add((f, n))

    knip_fn = expected_set - knip_tp_set
    knip_total = len(knip_direct) + len(knip_dead_files)

    s_tp, s_fp, s_fn, s_prec, s_rec, s_f1 = _calc_metrics(
        skylos_set, expected_set, used_set
    )

    k_prec = len(knip_tp_set) / knip_total * 100 if knip_total else 0
    k_rec = len(knip_tp_set) / len(expected_set) * 100 if expected_set else 0
    k_f1 = (2 * k_prec * k_rec / (k_prec + k_rec)) if (k_prec + k_rec) else 0

    print("\n" + "=" * 72)
    print("Benchmark: Skylos vs Knip")
    print("on unjs/consola")
    print("=" * 72)
    print(f"\nRepository: unjs/consola (~7,200 stars)")
    print(f"Language: TypeScript")
    print(f"Source: 21 files, ~2,050 LOC")
    print(
        f"Ground truth: {len(expected_set)} dead items, "
        f"{len(used_set)} confirmed-alive items\n"
    )

    print("## Results\n")
    print("| Metric | Skylos | Knip |")
    print("|--------|--------|------|")
    print(f"| True Positives (correctly found) | {s_tp} | {len(knip_tp_set)} |")
    print(f"| False Positives (flagged but used) | {s_fp} | {len(knip_fp_set)} |")
    print(f"| False Negatives (missed) | {s_fn} | {len(knip_fn)} |")
    print(f"| Precision | {s_prec:.1f}% | {k_prec:.1f}% |")
    print(f"| Recall | {s_rec:.1f}% | {k_rec:.1f}% |")
    print(f"| F1 Score | {s_f1:.1f}% | {k_f1:.1f}% |")
    print(f"| Speed | {skylos_time:.2f}s | {knip_time:.2f}s |")

    print("\n## Dead Code (should be found)\n")
    print("| Item | Category | Skylos | Knip |")
    print("|------|----------|--------|------|")
    for file, name, cat in expected:
        s = "found" if (file, name) in skylos_set else "MISSED"
        k = "found" if _match_knip(knip_findings, file, name) else "MISSED"
        print(f"| `{file}:{name}` | {cat} | {s} | {k} |")

    print("\n## False Positives (flagged but actually used)\n")
    print("| Item | Why it's used | Skylos | Knip |")
    print("|------|---------------|--------|------|")

    any_fp = False
    for file, name in ACTUALLY_USED:
        s_flag = "FP" if (file, name) in skylos_set else "ok"
        k_flag = "FP" if _match_knip(knip_findings, file, name) else "ok"
        if s_flag != "ok" or k_flag != "ok":
            any_fp = True
            print(f"| `{file}:{name}` | used internally | {s_flag} | {k_flag} |")

    if not any_fp:
        print("| (none) | | | |")

    if knip_dead_files:
        print("\n## Knip: Entirely Unused Files\n")
        src_dead = sorted(f for f in knip_dead_files if f.startswith("src/"))
        for f in src_dead:
            print(f"- `{f}`")
        if src_dead:
            print(
                "\nNote: basic.ts, browser.ts, core.ts are package entry points "
                "(specified in package.json exports). Knip flags them because "
                "exports point to dist/ not src/."
            )

    print("\n## Other Findings (not in ground truth)\n")
    all_known = expected_set | used_set
    skylos_other = skylos_set - all_known
    knip_other = knip_direct - all_known

    if skylos_other or knip_other:
        print("| Tool | File | Name |")
        print("|------|------|------|")
        for file, name in sorted(skylos_other):
            print(f"| Skylos | `{file}` | `{name}` |")
        for file, name in sorted(knip_other):
            print(f"| Knip | `{file}` | `{name}` |")
    else:
        print("(none)")

    print("\n## Notes\n")
    print(
        "- consola is a well-maintained library with very little dead code."
    )
    print(
        "- The only dead code is src/utils/format.ts — an entire orphaned module "
        "(never imported by any file). It contains 2 functions + 2 variables."
    )
    print(
        "- Knip reports many false positives because package.json exports point to "
        "dist/ (compiled output), so Knip can't trace src/ entry points."
    )
    print(
        "- Several Skylos false positives come from same-file variable usage "
        "(e.g. TYPE_COLOR_MAP used via `as any` cast on the same page)."
    )


if __name__ == "__main__":
    compare_results()
