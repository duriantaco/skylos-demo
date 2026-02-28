#!/usr/bin/env python3
"""
Benchmark: Skylos vs staticcheck on go-chi/chi (~18,000 stars).

Ground truth was manually verified by searching every symbol reference across
all .go files in the repository. The _examples/ directory is excluded since
it contains standalone demo programs, not shipped library code.

Run from the chi/ directory:
    cd real_life_examples/chi
    python3 ../benchmark_go_chi.py
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path


# Manually verified dead code in go-chi/chi.
# These are symbols defined but never referenced anywhere in the codebase.
EXPECTED_UNUSED = {
    "variables": [
        ("middleware/terminal.go", "nBlack"),
        ("middleware/terminal.go", "nBlue"),
        ("middleware/terminal.go", "nMagenta"),
        ("middleware/terminal.go", "nWhite"),
        ("middleware/terminal.go", "bBlack"),
    ],
    "functions": [
        ("tree_test.go", "debugPrintTree"),
    ],
    "classes": [],
}

# Symbols that look unused but are actually used (known false positives).
# These are included so we can measure precision.
ACTUALLY_USED = [
    # node.routes is called via chained selector mx.tree.routes() in mux.go.
    # AST-only analysis can't resolve chained selectors to their receiver type.
    ("tree.go", "routes"),
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
            file = file[len(cwd):].lstrip("/")
        elif file.startswith("/"):
            for prefix in ("middleware/", ""):
                marker = f"/chi/{prefix}" if prefix else "/chi/"
                if marker in file:
                    rest = file.split(marker, 1)[1]
                    file = (prefix + rest) if prefix else rest
                    break
        if file.startswith("./"):
            file = file[2:]
        if "." in name and "/" not in name and not name.startswith("_"):
            name = name.split(".")[-1]
        normalized.append((file, name, cat))
    return normalized


def run_skylos():
    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            [
                "skylos", ".",
                "--json",
                "--confidence", "20",
                "--exclude-folder", "_examples",
                "--no-default-excludes",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        duration = time.perf_counter() - start_time
        return _parse_skylos_output(result.stdout), duration
    except subprocess.TimeoutExpired:
        print("Skylos timed out after 120s")
        return [], 0.0
    except Exception as e:
        print(f"Skylos error: {e}")
        return [], 0.0


def _find_staticcheck():
    """Find staticcheck binary on PATH or in ~/go/bin."""
    import shutil
    found = shutil.which("staticcheck")
    if found:
        return found
    gobin = Path.home() / "go" / "bin" / "staticcheck"
    if gobin.is_file():
        return str(gobin)
    return None


def run_staticcheck():
    sc_bin = _find_staticcheck()
    if not sc_bin:
        print("staticcheck not found. Install: go install honnef.co/go/tools/cmd/staticcheck@latest")
        return [], 0.0

    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            [sc_bin, "-checks", "U1000", "./..."],
            capture_output=True,
            text=True,
            timeout=120,
        )
        duration = time.perf_counter() - start_time
        findings = []
        # staticcheck output: file.go:line:col: symbol is unused (U1000)
        pattern = r"^(.+?):(\d+):(\d+): (.+?) is unused \(U1000\)"
        for line in result.stdout.splitlines() + result.stderr.splitlines():
            match = re.match(pattern, line)
            if match:
                file = match.group(1).replace("\\", "/")
                if file.startswith("./"):
                    file = file[2:]
                symbol_desc = match.group(4)
                # Extract the simple name from descriptions like:
                #   "func debugPrintTree" -> "debugPrintTree"
                #   "var nBlack" -> "nBlack"
                #   "type Foo" -> "Foo"
                #   "field Bar" -> "Bar"
                parts = symbol_desc.strip().split()
                name = parts[-1] if parts else symbol_desc
                # Remove receiver prefix like "(*node)." from method names
                if "." in name:
                    name = name.split(".")[-1]
                kind = parts[0] if len(parts) > 1 else "unknown"
                cat_map = {
                    "func": "functions",
                    "var": "variables",
                    "const": "variables",
                    "type": "classes",
                    "field": "variables",
                    "method": "functions",
                }
                cat = cat_map.get(kind, "functions")
                findings.append((file, name, cat))
        return findings, duration
    except subprocess.TimeoutExpired:
        print("staticcheck timed out after 120s")
        return [], 0.0
    except Exception as e:
        print(f"staticcheck error: {e}")
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

    print("Running Skylos on go-chi/chi...")
    skylos_findings, skylos_time = run_skylos()
    skylos_set = {(f, n) for f, n, _ in skylos_findings}

    print("Running staticcheck on go-chi/chi...")
    sc_findings, sc_time = run_staticcheck()
    sc_set = {(f, n) for f, n, _ in sc_findings}

    s_tp, s_fp, s_fn, s_prec, s_rec, s_f1 = _calc_metrics(
        skylos_set, expected_set, used_set
    )
    c_tp, c_fp, c_fn, c_prec, c_rec, c_f1 = _calc_metrics(
        sc_set, expected_set, used_set
    )

    print("\n" + "=" * 72)
    print("Benchmark: Skylos vs staticcheck")
    print("on go-chi/chi")
    print("=" * 72)
    print(f"\nRepository: go-chi/chi (~18,000 stars)")
    print(f"Language: Go")
    print(
        f"Ground truth: {len(expected_set)} dead items, "
        f"{len(used_set)} confirmed-alive items\n"
    )

    print("## Results\n")
    print("| Metric | Skylos | staticcheck |")
    print("|--------|--------|-------------|")
    print(f"| True Positives (correctly found) | {s_tp} | {c_tp} |")
    print(f"| False Positives (flagged but used) | {s_fp} | {c_fp} |")
    print(f"| False Negatives (missed) | {s_fn} | {c_fn} |")
    print(f"| Precision | {s_prec:.1f}% | {c_prec:.1f}% |")
    print(f"| Recall | {s_rec:.1f}% | {c_rec:.1f}% |")
    print(f"| F1 Score | {s_f1:.1f}% | {c_f1:.1f}% |")
    print(f"| Speed | {skylos_time:.2f}s | {sc_time:.2f}s |")

    print("\n## Dead Code (should be found)\n")
    print("| Item | Category | Skylos | staticcheck |")
    print("|------|----------|--------|-------------|")
    for file, name, cat in expected:
        s = "found" if (file, name) in skylos_set else "MISSED"
        c = "found" if (file, name) in sc_set else "MISSED"
        print(f"| `{file}:{name}` | {cat} | {s} | {c} |")

    print("\n## False Positives (flagged but actually used)\n")
    print("| Item | Why it's used | Skylos | staticcheck |")
    print("|------|---------------|--------|-------------|")

    any_fp = False
    for file, name in ACTUALLY_USED:
        s_flag = "FP" if (file, name) in skylos_set else "ok"
        c_flag = "FP" if (file, name) in sc_set else "ok"
        if s_flag != "ok" or c_flag != "ok":
            any_fp = True
            print(f"| `{file}:{name}` | Chained selector / interface impl | {s_flag} | {c_flag} |")

    if not any_fp:
        print("| (none) | | | |")

    print("\n## Other Findings (not in ground truth)\n")
    all_known = expected_set | used_set
    skylos_other = skylos_set - all_known
    sc_other = sc_set - all_known

    if skylos_other or sc_other:
        print("| Tool | File | Name |")
        print("|------|------|------|")
        for file, name in sorted(skylos_other):
            print(f"| Skylos | `{file}` | `{name}` |")
        for file, name in sorted(sc_other):
            print(f"| staticcheck | `{file}` | `{name}` |")
    else:
        print("(none)")

    print("\n## Notes\n")
    print(
        "- go-chi/chi is a very well-maintained library with minimal dead code."
    )
    print(
        "- 5 dead items are unused ANSI terminal color variables in middleware/terminal.go."
    )
    print(
        "- 1 dead item is debugPrintTree in tree_test.go (debug helper never called)."
    )
    print(
        "- Other color variables (nRed, nGreen, nYellow, nCyan, bRed, bGreen, etc.) ARE used"
    )
    print("  in middleware/recoverer.go for formatting panic stack traces.")
    print(
        "- Skylos uses AST-only analysis (no Go type resolution), so it skips test file"
    )
    print(
        "  definitions by design. staticcheck uses full type info from the Go compiler."
    )
    print(
        "- Struct fields are not tracked as definitions by Skylos (too granular for v1)."
    )


if __name__ == "__main__":
    compare_results()
