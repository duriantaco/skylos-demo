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
        ("tests/compat.py", "u"),
        ("src/requests/cookies.py", "_find"),
        ("src/requests/utils.py", "dict_to_sequence"),
        ("src/requests/utils.py", "from_key_val_list"),
        ("src/requests/utils.py", "parse_list_header"),
    ],
    "variables": [
        ("src/requests/adapters.py", "DEFAULT_POOL_TIMEOUT"),
    ],
    "imports": [],
    "classes": [],
}

ACTUALLY_USED = [
    ("src/requests/api.py", "request"),
    ("src/requests/api.py", "get"),
    ("src/requests/api.py", "options"),
    ("src/requests/api.py", "head"),
    ("src/requests/api.py", "post"),
    ("src/requests/api.py", "put"),
    ("src/requests/api.py", "patch"),
    ("src/requests/api.py", "delete"),
    ("src/requests/sessions.py", "Session"),
    ("src/requests/sessions.py", "session"),
    ("src/requests/models.py", "Request"),
    ("src/requests/models.py", "Response"),
    ("src/requests/models.py", "PreparedRequest"),
    ("src/requests/exceptions.py", "URLRequired"),
    ("src/requests/sessions.py", "options"),
    ("src/requests/sessions.py", "head"),
    ("src/requests/sessions.py", "post"),
    ("src/requests/sessions.py", "put"),
    ("src/requests/sessions.py", "patch"),
    ("src/requests/sessions.py", "delete"),
    ("src/requests/models.py", "prepare"),
    ("src/requests/cookies.py", "list_domains"),
    ("src/requests/cookies.py", "list_paths"),
    ("src/requests/cookies.py", "multiple_domains"),
    ("src/requests/cookies.py", "get_dict"),
    ("src/requests/utils.py", "dict_from_cookiejar"),
    ("src/requests/utils.py", "get_unicode_from_response"),
    ("src/requests/compat.py", "simplejson"),
    ("src/requests/compat.py", "JSONDecodeError"),
    ("src/requests/compat.py", "OrderedDict"),
    ("src/requests/compat.py", "Callable"),
    ("src/requests/compat.py", "Mapping"),
    ("src/requests/compat.py", "MutableMapping"),
    ("src/requests/compat.py", "cookiejar"),
    ("src/requests/compat.py", "Morsel"),
    ("src/requests/compat.py", "StringIO"),
    ("src/requests/compat.py", "quote"),
    ("src/requests/compat.py", "quote_plus"),
    ("src/requests/compat.py", "unquote"),
    ("src/requests/compat.py", "unquote_plus"),
    ("src/requests/compat.py", "urldefrag"),
    ("src/requests/compat.py", "urlencode"),
    ("src/requests/compat.py", "urljoin"),
    ("src/requests/compat.py", "urlsplit"),
    ("src/requests/compat.py", "urlunparse"),
    ("src/requests/compat.py", "getproxies"),
    ("src/requests/compat.py", "getproxies_environment"),
    ("src/requests/compat.py", "parse_http_list"),
    ("src/requests/compat.py", "proxy_bypass"),
    ("src/requests/compat.py", "proxy_bypass_environment"),
    ("src/requests/compat.py", "is_py2"),
    ("src/requests/compat.py", "is_py3"),
    ("src/requests/compat.py", "numeric_types"),
    ("src/requests/_internal_utils.py", "HEADER_VALIDATORS"),
    ("src/requests/adapters.py", "SOCKSProxyManager"),
    ("src/requests/adapters.py", "_urllib3_request_context"),
    ("src/requests/utils.py", "proxy_bypass"),
    ("tests/test_utils.py", "TestSuperLen"),
    ("tests/test_utils.py", "TestGetNetrcAuth"),
    ("tests/test_utils.py", "TestToKeyValList"),
    ("tests/test_utils.py", "TestUnquoteHeaderValue"),
    ("tests/test_utils.py", "TestGetEnvironProxies"),
    ("tests/test_utils.py", "TestIsIPv4Address"),
    ("tests/test_utils.py", "TestIsValidCIDR"),
    ("tests/test_utils.py", "TestAddressInNetwork"),
    ("tests/test_utils.py", "TestGuessFilename"),
    ("tests/test_utils.py", "TestExtractZippedPaths"),
    ("tests/test_utils.py", "TestContentEncodingDetection"),
    ("tests/test_utils.py", "TestGuessJSONUTF"),
    ("tests/test_structures.py", "TestCaseInsensitiveDict"),
    ("tests/test_structures.py", "TestLookupDict"),
    ("tests/test_testserver.py", "TestTestServer"),
    ("tests/test_requests.py", "TestRequests"),
    ("tests/test_requests.py", "TestCaseInsensitiveDict"),
    ("tests/test_requests.py", "TestMorselToCookieExpires"),
    ("tests/test_requests.py", "TestMorselToCookieMaxAge"),
    ("tests/test_requests.py", "TestTimeout"),
    ("tests/test_requests.py", "TestPreparingURLs"),
    ("tests/test_utils.py", "tell"),
    ("tests/test_utils.py", "seek"),
    ("tests/test_utils.py", "Close"),
    ("tests/test_requests.py", "tell"),
    ("tests/test_requests.py", "seek"),
    ("tests/test_requests.py", "get_redirect_target"),
    ("tests/conftest.py", "HTTPServer"),
    ("tests/conftest.py", "SimpleHTTPRequestHandler"),
    ("tests/compat.py", "StringIO"),
    ("tests/compat.py", "io"),
    ("docs/conf.py", "extensions"),
    ("docs/conf.py", "templates_path"),
    ("docs/conf.py", "source_suffix"),
    ("docs/conf.py", "version"),
    ("docs/conf.py", "language"),
    ("docs/conf.py", "exclude_patterns"),
    ("docs/conf.py", "pygments_style"),
    ("docs/conf.py", "html_theme"),
    ("docs/conf.py", "html_theme_options"),
    ("docs/conf.py", "html_static_path"),
    ("docs/conf.py", "html_sidebars"),
    ("docs/conf.py", "htmlhelp_basename"),
    ("docs/conf.py", "latex_elements"),
    ("docs/conf.py", "latex_documents"),
    ("docs/conf.py", "man_pages"),
    ("docs/conf.py", "texinfo_documents"),
    ("docs/conf.py", "intersphinx_mapping"),
    ("docs/_themes/flask_theme_support.py", "FlaskyStyle"),
    ("docs/_themes/flask_theme_support.py", "background_color"),
    ("docs/_themes/flask_theme_support.py", "default_style"),
    ("docs/_themes/flask_theme_support.py", "styles"),
    ("tests/testserver/server.py", "run"),
    ("tests/testserver/server.py", "_create_socket_and_bind"),
    ("tests/testserver/server.py", "_handle_requests"),
    ("tests/testserver/server.py", "_accept_connection"),
    ("src/requests/cookies.py", "get_type"),
    ("src/requests/cookies.py", "get_full_url"),
    ("src/requests/cookies.py", "has_header"),
    ("src/requests/cookies.py", "get_header"),
    ("src/requests/cookies.py", "add_header"),
    ("src/requests/cookies.py", "add_unredirected_header"),
    ("src/requests/cookies.py", "getheaders"),
    ("src/requests/models.py", "_encode_files"),
    ("src/requests/models.py", "_encode_params"),
    ("src/requests/models.py", "deregister_hook"),
    ("docs/conf.py", "add_function_parentheses"),
    ("docs/conf.py", "add_module_names"),
    ("docs/conf.py", "todo_include_todos"),
    ("docs/conf.py", "html_use_smartypants"),
    ("docs/conf.py", "html_show_sourcelink"),
    ("docs/conf.py", "html_show_sphinx"),
    ("docs/conf.py", "html_show_copyright"),
    ("docs/conf.py", "epub_title"),
    ("docs/conf.py", "epub_author"),
    ("docs/conf.py", "epub_publisher"),
    ("docs/conf.py", "epub_copyright"),
    ("docs/conf.py", "epub_exclude_files"),
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
            for prefix in ("src/requests/", "tests/", "docs/"):
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
            [
                "skylos",
                "src/requests/",
                "tests/",
                "docs/",
                "--json",
                "--confidence",
                str(confidence),
            ],
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
            [
                "skylos",
                "src/requests/",
                "tests/",
                "docs/",
                "--json",
                "--trace",
                "--confidence",
                str(confidence),
            ],
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
            ["vulture", "src/requests/", "tests/", "docs/", "--min-confidence", "20"],
            capture_output=True,
            text=True,
        )
        end_time = time.perf_counter()
        duration = end_time - start_time

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
    print("=" * 72)
    print(f"\nRepository: psf/requests (~8,300 LOC, 53,800+ stars)")
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
        print(
            f"\n→ Trace mode eliminated {trace_eliminated} additional false positives over static analysis."
        )

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
        "api.py": "Public API (__init__.py export)",
        "sessions.py": "Public API (Session methods)",
        "models.py": "Public API (__init__.py export)",
        "exceptions.py": "Public API (__init__.py export)",
        "cookies.py": "Public API methods",
        "compat.py": "Backward-compat re-export",
        "_internal_utils.py": "Intentional re-export",
        "adapters.py": "try/except import pattern",
        "conf.py": "Sphinx config (execfile)",
        "flask_theme_support.py": "Pygments style (loaded by name)",
        "conftest.py": "Used in fixtures",
        "server.py": "Thread.start() dispatch",
    }

    any_fp = False
    for file, name in ACTUALLY_USED:
        s_flag = "FP" if (file, name) in skylos_set else "ok"
        t_flag = "FP" if (file, name) in trace_set else "ok"
        v_flag = "FP" if (file, name) in vulture_set else "ok"
        if s_flag != "ok" or t_flag != "ok" or v_flag != "ok":
            any_fp = True
            basename = file.split("/")[-1]
            reason = fp_reasons.get(basename, "Dynamic/protocol usage")
            if "test_" in basename:
                reason = "Pytest collection / duck-typing"
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
