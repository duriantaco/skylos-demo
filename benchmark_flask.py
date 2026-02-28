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
        ("src/flask/cli.py", "_path_is_ancestor"),
    ],
    "variables": [
        ("src/flask/templating.py", "_srcobj"),
        ("src/flask/typing.py", "BeforeFirstRequestCallable"),
    ],
    "imports": [],
    "classes": [
        ("src/flask/debughelpers.py", "UnexpectedUnicodeError"),
        ("tests/test_helpers.py", "PyBytesIO"),
        ("tests/test_apps/cliapp/multiapp.py", "app1"),
        ("tests/test_apps/cliapp/multiapp.py", "app2"),
    ],
}

ACTUALLY_USED = [
    ("src/flask/sansio/app.py", "shell_context_processor"),
    ("src/flask/sansio/scaffold.py", "patch"),
    ("src/flask/app.py", "open_instance_resource"),
    ("src/flask/sessions.py", "new"),
    ("src/flask/sessions.py", "popitem"),
    ("src/flask/sessions.py", "pickle_based"),
    ("src/flask/wrappers.py", "default_mimetype"),
    ("src/flask/wrappers.py", "autocorrect_location_header"),
    ("src/flask/wrappers.py", "json_module"),
    ("src/flask/app.py", "show_exception"),
    ("src/flask/config.py", "owner"),
    ("src/flask/ctx.py", "__getattr__"),
    ("src/flask/ctx.py", "exc_type"),
    ("src/flask/ctx.py", "json_module"),
    ("src/flask/globals.py", "__getattr__"),
    ("src/flask/helpers.py", "exc_tb"),
    ("src/flask/helpers.py", "exc_type"),
    ("src/flask/sansio/app.py", "extensions"),
    ("src/flask/testing.py", "exc_type"),
    ("src/flask/testing.py", "json_dumps"),
    ("src/flask/testing.py", "json_module"),
    ("tests/conftest.py", "_reset_os_environ"),
    ("tests/conftest.py", "leak_detector"),
    ("tests/conftest.py", "modules_tmp_path_prefix"),
    ("tests/test_config.py", "TEST_KEY"),
    ("tests/test_config.py", "SECRET_KEY"),
    ("tests/test_cli.py", "myapp1"),
    ("tests/test_cli.py", "myapp2"),
    ("tests/test_apps/cliapp/factory.py", "create_app2"),
    ("tests/test_apps/cliapp/factory.py", "no_app"),
    ("tests/test_apps/blueprintapp/apps/admin/__init__.py", "index2"),
    ("tests/test_apps/blueprintapp/apps/frontend/__init__.py", "missing_template"),
    ("tests/test_instance_config.py", "modules_tmp_path_prefix"),
    ("tests/test_blueprints.py", "test_apps"),
    ("tests/test_cli.py", "test_apps"),
    ("tests/test_templating.py", "test_apps"),
    ("tests/test_appctx.py", "cleanup"),
    ("tests/test_appctx.py", "teardown_req"),
    ("tests/test_appctx.py", "teardown_app"),
    ("tests/test_appctx.py", "request_teardown"),
    ("tests/test_appctx.py", "app_teardown"),
    ("tests/test_appctx.py", "sender"),
    ("tests/test_appctx.py", "spam"),
    ("tests/test_async.py", "_async_app"),
    ("tests/test_async.py", "handle"),
    ("tests/test_async.py", "bp_index"),
    ("tests/test_async.py", "bp_handle"),
    ("tests/test_async.py", "bp_error"),
    ("tests/test_async.py", "before"),
    ("tests/test_async.py", "after"),
    ("tests/test_async.py", "bp_before"),
    ("tests/test_async.py", "bp_after"),
    ("tests/test_basic.py", "index_put"),
    ("tests/test_basic.py", "do_set"),
    ("tests/test_basic.py", "do_get"),
    ("tests/test_basic.py", "do_nothing"),
    ("tests/test_basic.py", "set_session"),
    ("tests/test_basic.py", "get_session"),
    ("tests/test_basic.py", "modify_session"),
    ("tests/test_basic.py", "dump_session_contents"),
    ("tests/test_basic.py", "bump"),
    ("tests/test_basic.py", "getitem"),
    ("tests/test_basic.py", "vary_cookie_header_set"),
    ("tests/test_basic.py", "vary_header_set"),
    ("tests/test_basic.py", "no_vary_header"),
    ("tests/test_basic.py", "login"),
    ("tests/test_basic.py", "ignored"),
    ("tests/test_basic.py", "before_request1"),
    ("tests/test_basic.py", "before_request2"),
    ("tests/test_basic.py", "before_request3"),
    ("tests/test_basic.py", "teardown_request1"),
    ("tests/test_basic.py", "teardown_request2"),
    ("tests/test_basic.py", "fails"),
    ("tests/test_basic.py", "before1"),
    ("tests/test_basic.py", "before2"),
    ("tests/test_basic.py", "after1"),
    ("tests/test_basic.py", "after2"),
    ("tests/test_basic.py", "finish1"),
    ("tests/test_basic.py", "finish2"),
    ("tests/test_basic.py", "not_found"),
    ("tests/test_basic.py", "internal_server_error"),
    ("tests/test_basic.py", "forbidden"),
    ("tests/test_basic.py", "error2"),
    ("tests/test_basic.py", "broken_func"),
    ("tests/test_basic.py", "attach_something"),
    ("tests/test_basic.py", "return_something"),
    ("tests/test_basic.py", "handle_my_exception"),
    ("tests/test_basic.py", "handle_forbidden_subclass"),
    ("tests/test_basic.py", "handle_403"),
    ("tests/test_basic.py", "index1"),
    ("tests/test_basic.py", "index2"),
    ("tests/test_basic.py", "index3"),
    ("tests/test_basic.py", "handle_e2"),
    ("tests/test_basic.py", "raise_e1"),
    ("tests/test_basic.py", "raise_e3"),
    ("tests/test_basic.py", "fail"),
    ("tests/test_basic.py", "allow_abort"),
    ("tests/test_basic.py", "from_text"),
    ("tests/test_basic.py", "from_bytes"),
    ("tests/test_basic.py", "from_full_tuple"),
    ("tests/test_basic.py", "from_text_headers"),
    ("tests/test_basic.py", "from_text_status"),
    ("tests/test_basic.py", "from_response_headers"),
    ("tests/test_basic.py", "from_response_status"),
    ("tests/test_basic.py", "from_wsgi"),
    ("tests/test_basic.py", "from_dict"),
    ("tests/test_basic.py", "from_list"),
    ("tests/test_basic.py", "from_none"),
    ("tests/test_basic.py", "from_small_tuple"),
    ("tests/test_basic.py", "from_large_tuple"),
    ("tests/test_basic.py", "from_bad_type"),
    ("tests/test_basic.py", "from_bad_wsgi"),
    ("tests/test_basic.py", "catch_all"),
    ("tests/test_basic.py", "add_language_code"),
    ("tests/test_basic.py", "pull_lang_code"),
    ("tests/test_basic.py", "about"),
    ("tests/test_basic.py", "something_else"),
    ("tests/test_basic.py", "bp_defaults"),
    ("tests/test_basic.py", "for_bar"),
    ("tests/test_basic.py", "for_bar_foo"),
    ("tests/test_basic.py", "normal_index"),
    ("tests/test_blueprints.py", "frontend_forbidden"),
    ("tests/test_blueprints.py", "frontend_no"),
    ("tests/test_blueprints.py", "backend_forbidden"),
    ("tests/test_blueprints.py", "backend_no"),
    ("tests/test_blueprints.py", "sideend_no"),
    ("tests/test_blueprints.py", "app_forbidden"),
    ("tests/test_blueprints.py", "my_decorator_exception_handler"),
    ("tests/test_blueprints.py", "blue_deco_test"),
    ("tests/test_blueprints.py", "blue_func_test"),
    ("tests/test_blueprints.py", "forbidden_handler"),
    ("tests/test_blueprints.py", "bp_forbidden"),
    ("tests/test_blueprints.py", "add_language_code"),
    ("tests/test_blueprints.py", "pull_lang_code"),
    ("tests/test_blueprints.py", "about"),
    ("tests/test_blueprints.py", "app_index"),
    ("tests/test_blueprints.py", "foo_bar"),
    ("tests/test_blueprints.py", "foo_bar_foo"),
    ("tests/test_blueprints.py", "bar_foo"),
    ("tests/test_blueprints.py", "foobar"),
    ("tests/test_blueprints.py", "not_answer_context_processor"),
    ("tests/test_blueprints.py", "answer_context_processor"),
    ("tests/test_blueprints.py", "bp_page"),
    ("tests/test_blueprints.py", "app_page"),
    ("tests/test_blueprints.py", "before_bp"),
    ("tests/test_blueprints.py", "after_bp"),
    ("tests/test_blueprints.py", "teardown_bp"),
    ("tests/test_blueprints.py", "bp_endpoint"),
    ("tests/test_blueprints.py", "before_app"),
    ("tests/test_blueprints.py", "after_app"),
    ("tests/test_blueprints.py", "teardown_app"),
    ("tests/test_blueprints.py", "child_before1"),
    ("tests/test_blueprints.py", "child_before2"),
    ("tests/test_blueprints.py", "child_ctx"),
    ("tests/test_blueprints.py", "child_teardown1"),
    ("tests/test_blueprints.py", "child_teardown2"),
    ("tests/test_blueprints.py", "parent_before1"),
    ("tests/test_blueprints.py", "parent_before2"),
    ("tests/test_blueprints.py", "parent_ctx"),
    ("tests/test_blueprints.py", "parent_teardown1"),
    ("tests/test_blueprints.py", "parent_teardown2"),
    ("tests/test_blueprints.py", "app_before1"),
    ("tests/test_blueprints.py", "app_before2"),
    ("tests/test_blueprints.py", "app_teardown1"),
    ("tests/test_blueprints.py", "app_teardown2"),
    ("tests/test_blueprints.py", "a"),
    ("tests/test_blueprints.py", "b"),
    ("tests/test_blueprints.py", "allow_subdomain_redirects"),
    ("tests/test_blueprints.py", "forbidden"),
    ("tests/test_blueprints.py", "parent_index"),
    ("tests/test_blueprints.py", "parent_no"),
    ("tests/test_blueprints.py", "child_index"),
    ("tests/test_blueprints.py", "child_no"),
    ("tests/test_blueprints.py", "grandchild_forbidden"),
    ("tests/test_blueprints.py", "grandchild_index"),
    ("tests/test_blueprints.py", "grandchild_no"),
    ("tests/test_blueprints.py", "index2"),
    ("tests/test_cli.py", "make_app"),
    ("tests/test_cli.py", "test2"),
    ("tests/test_cli.py", "custom_command"),
    ("tests/test_cli.py", "nested_command"),
    ("tests/test_cli.py", "merged_command"),
    ("tests/test_cli.py", "late_command"),
    ("tests/test_json.py", "post_json"),
    ("tests/test_json.py", "return_json"),
    ("tests/test_json.py", "return_kwargs"),
    ("tests/test_json.py", "return_dict"),
    ("tests/test_json.py", "return_args_unpack"),
    ("tests/test_json.py", "return_array"),
    ("tests/test_json.py", "utcoffset"),
    ("tests/test_json.py", "tzname"),
    ("tests/test_json.py", "dst"),
    ("tests/test_json.py", "_has_encoding"),
    ("tests/test_logging.py", "reset_logging"),
    ("tests/test_regression.py", "handle_foo"),
    ("tests/test_reqctx.py", "end_of_request"),
    ("tests/test_reqctx.py", "sub"),
    ("tests/test_reqctx.py", "set_dynamic_cookie"),
    ("tests/test_reqctx.py", "get_dynamic_cookie"),
    ("tests/test_request.py", "catcher"),
    ("tests/test_signals.py", "sender"),
    ("tests/test_signals.py", "before_request_handler"),
    ("tests/test_signals.py", "after_request_handler"),
    ("tests/test_templating.py", "handle"),
    ("tests/test_testing.py", "get_session"),
    ("tests/test_testing.py", "action"),
    ("tests/test_user_error_handler.py", "Custom"),
    ("tests/test_user_error_handler.py", "custom_exception_handler"),
    ("tests/test_user_error_handler.py", "handle_500"),
    ("tests/test_user_error_handler.py", "custom_test"),
    ("tests/test_user_error_handler.py", "key_error"),
    ("tests/test_user_error_handler.py", "do_abort"),
    ("tests/test_user_error_handler.py", "parent_exception_handler"),
    ("tests/test_user_error_handler.py", "child_exception_handler"),
    ("tests/test_user_error_handler.py", "parent_test"),
    ("tests/test_user_error_handler.py", "unregistered_test"),
    ("tests/test_user_error_handler.py", "registered_test"),
    ("tests/test_user_error_handler.py", "code_exception_handler"),
    ("tests/test_user_error_handler.py", "subclass_exception_handler"),
    ("tests/test_user_error_handler.py", "forbidden_test"),
    ("tests/test_user_error_handler.py", "bp_exception_handler"),
    ("tests/test_user_error_handler.py", "bp_test"),
    ("tests/test_user_error_handler.py", "app_exception_handler"),
    ("tests/test_user_error_handler.py", "app_test"),
    ("tests/test_user_error_handler.py", "bp_forbidden_handler"),
    ("tests/test_user_error_handler.py", "bp_registered_test"),
    ("tests/test_user_error_handler.py", "bp_forbidden_test"),
    ("tests/test_user_error_handler.py", "catchall_exception_handler"),
    ("tests/test_user_error_handler.py", "catchall_forbidden_handler"),
    ("tests/test_user_error_handler.py", "forbidden"),
    ("tests/test_user_error_handler.py", "slash"),
    ("tests/test_user_error_handler.py", "do_custom"),
    ("tests/test_user_error_handler.py", "do_error"),
    ("tests/test_user_error_handler.py", "do_raise"),
    ("tests/test_user_error_handler.py", "handle_http"),
    ("tests/test_views.py", "propfind"),
    ("tests/type_check/typing_app_decorators.py", "after_sync"),
    ("tests/type_check/typing_app_decorators.py", "after_async"),
    ("tests/type_check/typing_app_decorators.py", "before_sync"),
    ("tests/type_check/typing_app_decorators.py", "before_async"),
    ("tests/type_check/typing_app_decorators.py", "teardown_sync"),
    ("tests/type_check/typing_app_decorators.py", "teardown_async"),
    ("tests/type_check/typing_error_handler.py", "handle_400"),
    ("tests/type_check/typing_error_handler.py", "handle_custom"),
    ("tests/type_check/typing_error_handler.py", "handle_accept_base"),
    ("tests/type_check/typing_error_handler.py", "handle_multiple"),
    ("tests/type_check/typing_route.py", "hello_str"),
    ("tests/type_check/typing_route.py", "hello_bytes"),
    ("tests/type_check/typing_route.py", "hello_json"),
    ("tests/type_check/typing_route.py", "hello_json_dict"),
    ("tests/type_check/typing_route.py", "hello_json_list"),
    ("tests/type_check/typing_route.py", "typed_dict"),
    ("tests/type_check/typing_route.py", "hello_generator"),
    ("tests/type_check/typing_route.py", "hello_generator_expression"),
    ("tests/type_check/typing_route.py", "hello_iterator"),
    ("tests/type_check/typing_route.py", "tuple_status"),
    ("tests/type_check/typing_route.py", "tuple_status_enum"),
    ("tests/type_check/typing_route.py", "tuple_headers"),
    ("tests/type_check/typing_route.py", "return_template"),
    ("tests/type_check/typing_route.py", "return_template_stream"),
    ("tests/type_check/typing_route.py", "async_route"),
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
            for prefix in ("src/flask/", "tests/"):
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
            ["skylos", "src/flask/", "tests/", "--json", "--confidence", str(confidence)],
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
                "src/flask/",
                "tests/",
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
            ["vulture", "src/flask/", "tests/", "--min-confidence", "20"],
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
    print("on pallets/flask")
    print("=" * 72)
    print(f"\nRepository: pallets/flask (~69,000 stars)")
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

    any_fp = False
    for file, name in ACTUALLY_USED:
        s_flag = "FP" if (file, name) in skylos_set else "ok"
        t_flag = "FP" if (file, name) in trace_set else "ok"
        v_flag = "FP" if (file, name) in vulture_set else "ok"
        if s_flag != "ok" or t_flag != "ok" or v_flag != "ok":
            any_fp = True
            basename = file.split("/")[-1]
            if "test_" in basename or "conftest" in basename:
                reason = "Flask decorator / fixture"
            elif "type_check" in file:
                reason = "Type checking test"
            elif basename in ("factory.py", "multiapp.py", "__init__.py"):
                reason = "CLI / blueprint registration"
            else:
                reason = "Public API / class attribute"
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
