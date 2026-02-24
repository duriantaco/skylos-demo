#!/usr/bin/env python3
import argparse
import subprocess
import json
import re
import time
import tempfile
from pathlib import Path

DEFAULT_CONFIDENCE = 10

EXPECTED_UNUSED = {
    "imports": [
        ("app/logging.py", "math"),
        ("app/api/routers/notes.py", "datetime"),
        ("app/api/deps.py", "get_settings"),
        ("app/api/deps.py", "Session"),
        ("app/api/routers/reports.py", "fmt_money"),
        ("app/integrations/bootstrap.py", "flask"),
        ("app/integrations/bootstrap.py", "sys"),
        ("app/integrations/slack.py", "Tuple"),
    ],
    "functions": [
        ("app/config.py", "_is_prod"),
        ("app/api/deps.py", "get_actor_from_headers"),
        ("app/api/routers/notes.py", "_normalize_query"),
        ("app/api/routers/reports.py", "generate_report"),
        ("app/db/session.py", "_drop_all"),
        ("app/db/crud.py", "_row_to_dict"),
        ("app/services/notes_services.py", "_validate_title"),
        ("app/services/notes_services.py", "normalize_and_score_query"),
        ("app/utils/ids.py", "slugify"),
        ("app/utils/ids.py", "new_request_id"),
        ("app/utils/ids.py", "weak_token"),
        ("app/utils/formatters.py", "format_money"),
        ("app/services/payment_services.py", "process"),
        ("app/services/payment_services.py", "run_payment"),
        ("app/core/errors.py", "not_found"),
        ("app/integrations/http_client.py", "request_text"),
        ("app/integrations/webhook_signing.py", "verify_hmac_sha256_prefixed"),
        ("app/integrations/slack.py", "build_finding_blocks"),
        ("app/integrations/github.py", "find_issue_by_title"),
        ("app/integrations/metrics.py", "timed_request"),
        ("app/integrations/metrics.py", "snapshot_metrics"),
        ("app/integrations/metrics.py", "add_tags"),
        ("app/services/report_service.py", "_build_header"),
        ("app/services/report_service.py", "_build_footer"),
        ("app/services/report_service.py", "generate_report_v1"),
        ("app/services/report_service.py", "_search_v2"),
        # --- new enterprise patterns ---
        ("app/core/middleware.py", "generate_correlation_id"),
        ("app/core/decorators.py", "validate_input"),
        ("app/core/decorators.py", "deprecate"),
        ("app/services/tasks.py", "generate_daily_report"),
        ("app/services/tasks.py", "sync_external_contacts"),
        ("app/services/tasks.py", "cleanup_expired_sessions"),
        ("app/core/cache.py", "invalidate_cache_for"),
        ("app/core/feature_flags.py", "get_all_flags"),
        ("app/core/feature_flags.py", "_evaluate_flag_with_context"),
        ("app/core/events.py", "on_note_deleted_cleanup"),
        ("app/core/events.py", "on_user_signed_up_welcome"),
        ("app/core/pagination.py", "apply_filters"),
        ("app/core/auth.py", "validate_bearer_token"),
        ("app/core/auth.py", "generate_api_token"),
        ("app/core/auth.py", "check_ip_allowlist"),
        ("app/core/plugins.py", "list_plugins"),
        ("app/core/plugins.py", "unload_plugin"),
        ("tests/conftest.py", "mock_redis"),
        ("tests/conftest.py", "admin_user"),
        ("tests/factories.py", "random_email"),
        ("tests/helpers.py", "assert_paginated_response"),
        ("tests/helpers.py", "wait_for_event"),
        ("tests/helpers.py", "mock_external_service"),
        ("tests/test_notes.py", "test_create_note_with_tags"),
        ("tests/test_notes.py", "test_bulk_import_notes"),
        ("tests/test_notes.py", "_seed_notes"),
        ("app/services/notification_service.py", "send_bulk_notifications"),
        ("app/services/notification_service.py", "schedule_notification"),
        ("app/services/notification_service.py", "_render_template"),
        ("app/services/audit_service.py", "query_audit_log"),
        ("app/services/audit_service.py", "_redact_sensitive_fields"),
        ("app/services/audit_service.py", "export_audit_csv"),
        ("app/config.py", "_parse_cors_origins"),
        ("app/db/crud.py", "bulk_create_notes"),
        ("app/db/crud.py", "_build_search_query"),
        ("app/db/session.py", "get_engine_info"),
        ("app/db/session.py", "_reset_sequences"),
    ],
    "variables": [
        ("app/main.py", "APP_DISPLAY_NAME"),
        ("app/db/crud.py", "DEFAULT_PAGE_SIZE"),
        ("app/utils/ids.py", "DEFAULT_REQUEST_ID"),
        ("app/integrations/http_client.py", "DEFAULT_HEADERS"),
        ("app/integrations/metrics.py", "_queue_depth"),
        ("app/services/tasks.py", "TASK_PRIORITY_HIGH"),
        ("app/services/tasks.py", "TASK_PRIORITY_LOW"),
        ("app/core/feature_flags.py", "FLAG_ADMIN_ENDPOINT"),
        ("app/core/events.py", "EVENT_NOTE_ARCHIVED"),
        ("app/core/auth.py", "ROLE_VIEWER"),
        ("app/core/auth.py", "TOKEN_ALGORITHM"),
        ("tests/conftest.py", "TEST_TIMEOUT"),
        ("tests/helpers.py", "SLOW_TEST_THRESHOLD"),
        ("app/services/notification_service.py", "MAX_BATCH_SIZE"),
        ("app/services/audit_service.py", "AUDIT_RETENTION_DAYS"),
        ("app/config.py", "MAX_UPLOAD_SIZE"),
        ("app/db/session.py", "DB_POOL_SIZE"),
    ],
    "classes": [
        ("app/core/errors.py", "DemoError"),
        ("app/db/models.py", "Tag"),
        ("app/schemas/notes.py", "NoteInternal"),
        ("app/services/payment_services.py", "PayPal"),
        ("app/core/middleware.py", "CorrelationIdMiddleware"),
        ("app/core/middleware.py", "RateLimitMiddleware"),
        ("app/core/base.py", "MongoNoteRepository"),
        ("app/core/base.py", "PagerDutyNotifier"),
        ("app/core/cache.py", "RedisCache"),
        ("app/core/exceptions.py", "AuthenticationError"),
        ("app/core/exceptions.py", "AuthorizationError"),
        ("app/core/exceptions.py", "RateLimitError"),
        ("app/core/exceptions.py", "ExternalServiceError"),
        ("app/core/pagination.py", "CursorParams"),
        ("app/core/pagination.py", "CursorResult"),
        ("tests/factories.py", "UserFactory"),
        ("tests/factories.py", "TagFactory"),
        ("app/services/notification_service.py", "NotificationLog"),
        ("app/db/models.py", "Comment"),
        ("app/db/models.py", "Attachment"),
        ("app/schemas/notes.py", "NotePatch"),
        ("app/schemas/notes.py", "NoteSearch"),
    ],
}

DYNAMIC_FALSE_POSITIVES = [
    ("app/services/export_service.py", "export_csv"),
    ("app/services/export_service.py", "export_json"),
    ("app/services/export_service.py", "export_xml"),
    ("app/api/handlers.py", "handle_create"),
    ("app/api/handlers.py", "handle_update"),
    ("app/api/handlers.py", "handle_delete"),
    ("app/core/registry.py", "EmailHandler"),
    ("app/core/registry.py", "SlackAlertHandler"),
    ("app/services/tasks.py", "send_welcome_email"),
    ("app/core/events.py", "on_note_created_log"),
    ("app/core/events.py", "on_note_created_notify"),
    ("app/services/notification_service.py", "_dispatch_email"),
    ("app/services/notification_service.py", "_dispatch_slack"),
    ("app/services/notification_service.py", "_dispatch_sms"),
]

ACTUALLY_USED = [
    ("app/main.py", "create_app"),
    ("app/main.py", "app"),
    ("app/api/deps.py", "get_db"),
    ("app/api/deps.py", "require_api_key"),
    ("app/db/crud.py", "create_note"),
    ("app/db/crud.py", "list_notes"),
    ("app/db/crud.py", "search_notes"),
    ("app/db/session.py", "init_db"),
    ("app/db/session.py", "SessionLocal"),
    ("app/db/models.py", "Base"),
    ("app/db/models.py", "Note"),
    ("app/config.py", "get_settings"),
    ("app/config.py", "Settings"),
    ("app/schemas/notes.py", "NoteCreate"),
    ("app/schemas/notes.py", "NoteOut"),
    ("app/services/notes_services.py", "create_note"),
    ("app/services/notes_services.py", "list_notes"),
    ("app/services/notes_services.py", "search_notes"),
    ("app/logging.py", "configure_logging"),
    ("app/api/routers/health.py", "router"),
    ("app/api/routers/notes.py", "router"),
    ("app/api/routers/__init__.py", "api_router"),
    ("app/integrations/bootstrap.py", "init_integrations"),
    ("app/integrations/routers/webhooks.py", "router"),
    ("app/integrations/routers/webhooks.py", "demo_webhook"),
    ("app/integrations/webhook_signing.py", "verify_hmac_sha256"),
    ("app/integrations/metrics.py", "record_request"),
    ("app/integrations/metrics.py", "record_latency_ms"),
    ("app/services/export_service.py", "run_export"),
    ("app/services/export_service.py", "export_csv"),
    ("app/services/export_service.py", "export_json"),
    ("app/services/export_service.py", "export_xml"),
    ("app/api/handlers.py", "dispatch"),
    ("app/api/handlers.py", "handle_create"),
    ("app/api/handlers.py", "handle_update"),
    ("app/api/handlers.py", "handle_delete"),
    ("app/core/registry.py", "get_handler"),
    ("app/core/registry.py", "EmailHandler"),
    ("app/core/registry.py", "SlackAlertHandler"),
    ("app/services/report_service.py", "search"),
    ("app/core/middleware.py", "RequestLoggingMiddleware"),
    ("app/core/decorators.py", "retry"),
    ("app/core/decorators.py", "log_execution"),
    ("app/core/base.py", "NoteRepository"),
    ("app/core/base.py", "SqlNoteRepository"),
    ("app/core/base.py", "Notifier"),
    ("app/core/base.py", "SlackNotifier"),
    ("app/services/tasks.py", "send_welcome_email"),
    ("app/services/tasks.py", "purge_soft_deletes"),
    ("app/core/cache.py", "InMemoryCache"),
    ("app/core/cache.py", "cached"),
    ("app/core/feature_flags.py", "is_enabled"),
    ("app/core/exceptions.py", "AppException"),
    ("app/core/exceptions.py", "ValidationError"),
    ("app/core/exceptions.py", "NotFoundError"),
    ("app/core/events.py", "EventBus"),
    ("app/core/events.py", "on_note_created_log"),
    ("app/core/events.py", "on_note_created_notify"),
    ("app/core/pagination.py", "PageParams"),
    ("app/core/pagination.py", "PageResult"),
    ("app/core/pagination.py", "paginate"),
    ("app/core/auth.py", "hash_api_key"),
    ("app/core/auth.py", "verify_api_key"),
    ("app/core/auth.py", "ROLE_ADMIN"),
    ("app/core/plugins.py", "load_plugin"),
    ("app/core/plugins.py", "get_plugin"),
    ("app/services/tasks.py", "run_task"),
    ("app/core/middleware.py", "dispatch"),
    ("app/core/base.py", "create"),
    ("app/core/base.py", "find_by_id"),
    ("app/core/base.py", "list_all"),
    ("app/core/base.py", "send"),
    # --- tests ---
    ("tests/conftest.py", "db_session"),
    ("tests/conftest.py", "test_client"),
    ("tests/conftest.py", "api_key_header"),
    ("tests/factories.py", "NoteFactory"),
    ("tests/helpers.py", "assert_json_response"),
    ("tests/helpers.py", "create_test_note"),
    ("tests/test_notes.py", "test_create_note"),
    ("tests/test_notes.py", "test_list_notes"),
    ("tests/test_notes.py", "test_search_notes"),
    ("app/db/models.py", "AuditLog"),
    ("app/schemas/notes.py", "NoteUpdate"),
    ("app/db/crud.py", "update_note"),
    ("app/db/crud.py", "delete_note"),
    ("app/db/crud.py", "get_note_by_id"),
    ("app/services/notification_service.py", "send_notification"),
    ("app/services/notification_service.py", "NotificationChannel"),
    ("app/services/notification_service.py", "_dispatch_email"),
    ("app/services/notification_service.py", "_dispatch_slack"),
    ("app/services/notification_service.py", "_dispatch_sms"),
    ("app/services/audit_service.py", "log_action"),
    ("app/services/audit_service.py", "AuditEntry"),
]

def get_all_expected():
    items = []
    for category, entries in EXPECTED_UNUSED.items():
        for file, name in entries:
            items.append((file, name, category))
    return items

def canonicalize(file: str, name: str) -> tuple[str, str]:
    file = file.replace("\\", "/")
    if file.startswith("./"):
        file = file[2:]
    if file == "app/api/routers/reports.py" and name == "format_money":
        name = "fmt_money"
    return file, name

def _relativize_path(p: str) -> str:
    import os
    cwd = os.getcwd().replace("\\", "/")
    p = (p or "").replace("\\", "/")
    if p.startswith(cwd):
        p = p[len(cwd):].lstrip("/")
    if p.startswith("./"):
        p = p[2:]
    return p

def run_skylos_static(confidence=DEFAULT_CONFIDENCE):
    start = time.perf_counter()
    result = subprocess.run(
        ["skylos", "app/", "tests/", "--json", "--confidence", str(confidence)],
        capture_output=True,
        text=True,
    )
    dur = time.perf_counter() - start

    if result.returncode != 0:
        raise RuntimeError(f"skylos static failed (exit={result.returncode}):\n{result.stderr[:800]}")

    data = json.loads(result.stdout or "{}")

    findings = []
    for item in data.get("unused_functions", []):
        findings.append((_relativize_path(item.get("file", "")), item.get("simple_name") or item.get("name") or "", "functions"))
    for item in data.get("unused_imports", []):
        findings.append((_relativize_path(item.get("file", "")), item.get("simple_name") or item.get("name") or "", "imports"))
    for item in data.get("unused_variables", []):
        findings.append((_relativize_path(item.get("file", "")), item.get("simple_name") or item.get("name") or "", "variables"))
    for item in data.get("unused_classes", []):
        findings.append((_relativize_path(item.get("file", "")), item.get("simple_name") or item.get("name") or "", "classes"))

    out = []
    for file, name, cat in findings:
        file = file.replace("\\", "/")
        if not file.startswith("app/") and not file.startswith("tests/"):
            continue
        name = str(name)
        if "." in name and "/" not in name and not name.startswith("_"):
            name = name.split(".")[-1]
        file, name = canonicalize(file, name)
        out.append((file, name, cat))

    return out, dur

def run_skylos_hybrid_json():
    out_path = Path(tempfile.gettempdir()) / "skylos_hybrid.json"

    start = time.perf_counter()
    result = subprocess.run(
        ["skylos", "agent", "analyze", ".", "--format", "json", "--min-confidence", "low", "--output", str(out_path)],
        capture_output=True,
        text=True,
    )
    dur = time.perf_counter() - start

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(
            f"hybrid produced no JSON file (exit={result.returncode}). stderr:\n{result.stderr[:800]}"
        )

    data = json.load(open(out_path, "r", encoding="utf-8"))

    def _cat(f: dict) -> str:
        return str(f.get("category") or f.get("_category") or "").strip().lower()

    def _src(f: dict) -> str:
        return str(f.get("source") or f.get("_source") or "").strip().lower()

    def _typ(f: dict) -> str:
        return str(f.get("type") or "").strip().lower()

    def _is_deadcode_like(f: dict) -> bool:
        c = _cat(f)
        rid = str(f.get("rule_id", "")).strip().upper()
        msg = str(f.get("message", "")).strip().lower()
        t = _typ(f)

        if c in ("dead_code", "deadcode", "dead-code"):
            return True
        if c.startswith("dead"):
            return True
        if rid.startswith("SKY-DC"):
            return True
        if "unused" in msg and t in ("function", "import", "variable", "class"):
            return True
        return False

    def _deadcode_cat(f: dict) -> str:
        t = _typ(f)
        if t == "function": 
            return "functions"
        if t == "import": 
            return "imports"
        if t == "variable": 
            return "variables"
        if t == "class": 
            return "classes"
        return "unknown"

    def _name(f: dict) -> str:
        n = f.get("simple_name") or f.get("name") or f.get("symbol") or ""
        n = str(n)
        if "." in n and "/" not in n:
            left, right = n.split(".", 1)
            if left[:1].isupper():
                n = right.split(".")[-1]
        return n

    deadcode_all = []
    deadcode_agree = []
    deadcode_llm_only = []
    deadcode_static_only = []

    for f in data or []:
        if not isinstance(f, dict):
            continue
        if not _is_deadcode_like(f):
            continue

        file = _relativize_path(f.get("file") or "").replace("\\", "/")
        if not file.startswith("app/") and not file.startswith("tests/"):
            continue

        name = _name(f)
        file, name = canonicalize(file, name)
        tup = (file, name, _deadcode_cat(f))

        src = _src(f)
        is_high_conf = src == "static+llm"
        deadcode_all.append(tup)
        if src == "llm":
            deadcode_llm_only.append(tup)
        elif is_high_conf:
            deadcode_agree.append(tup)
        else:
            deadcode_static_only.append(tup)

    return deadcode_all, deadcode_agree, deadcode_llm_only, deadcode_static_only, dur

def run_vulture():
    start_time = time.perf_counter()

    result = subprocess.run(
        ["vulture", "app/", "tests/", "--min-confidence", "20"],
        capture_output=True,
        text=True,
    )

    end_time = time.perf_counter()
    duration = end_time - start_time

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    findings = []
    pattern = r"(.+?):(\d+): unused (\w+) '(\w+)'" 

    for line in stdout.splitlines():
        m = re.search(pattern, line)
        if not m:
            continue

        file = m.group(1).replace("\\", "/")
        if file.startswith("./"):
            file = file[2:]
        kind = m.group(3)
        name = m.group(4)

        cat_map = {
            "function": "functions",
            "variable": "variables",
            "import": "imports",
            "class": "classes",
            "attribute": "variables",
        }
        cat = cat_map.get(kind, kind)
        findings.append((file, name, cat))

    if result.returncode not in (0, 1):
        print(
            "Vulture warning: non-success exit code, but stdout contained findings.\n"
            f"exit={result.returncode}\n"
            f"STDERR(head):\n{stderr[:800]}\n"
            f"STDERR(tail):\n{stderr[-800:]}\n"
            f"STDOUT(tail):\n{stdout[-800:]}\n"
        )

        if not findings:
            raise RuntimeError(
                f"vulture failed (exit={result.returncode}) and produced no parseable findings.\n"
                f"STDERR(tail):\n{stderr[-2000:]}\n"
                f"STDOUT(tail):\n{stdout[-2000:]}"
            )

    return findings, duration



def _metrics(found_set, expected_set, used_set):
    tp = found_set & expected_set
    fp = found_set & used_set
    fn = expected_set - found_set
    if found_set:
        prec = (len(tp) / len(found_set) * 100)
    else:
        prec = 0.0

    if expected_set:
        rec = (len(tp) / len(expected_set) * 100)
    else:
        rec = 0.0

    return tp, fp, fn, prec, rec

def compare_results(confidence=DEFAULT_CONFIDENCE):
    expected = get_all_expected()
    expected_set = {(f, n) for f, n, _ in expected}
    used_set = {(f, n) for f, n in ACTUALLY_USED}

    skylos_static, t_static = run_skylos_static(confidence=confidence)

    dead_all, dead_agree, dead_llm_only, dead_static_only, t_hybrid = run_skylos_hybrid_json()

    skylos_hybrid = dead_all

    vulture_findings, t_vulture = run_vulture()

    s_static_set    = {(f, n) for f, n, _ in skylos_static}
    s_hybrid_set    = {(f, n) for f, n, _ in skylos_hybrid}
    s_agree_set     = {(f, n) for f, n, _ in dead_agree}
    s_llm_only_set  = {(f, n) for f, n, _ in dead_llm_only}
    s_static_only_set = {(f, n) for f, n, _ in dead_static_only}
    v_set           = {(f, n) for f, n, _ in vulture_findings}

    s_tp, s_fp, s_fn, s_prec, s_rec = _metrics(s_static_set, expected_set, used_set)
    h_tp, h_fp, h_fn, h_prec, h_rec = _metrics(s_hybrid_set, expected_set, used_set)
    a_tp, a_fp, a_fn, a_prec, a_rec = _metrics(s_agree_set, expected_set, used_set)
    v_tp, v_fp, v_fn, v_prec, v_rec = _metrics(v_set, expected_set, used_set)

    print("\n## Benchmark Results (Dead Code — Python)\n")
    print("| Metric | Skylos Static | Skylos Hybrid | Hybrid High-Conf (static∩llm) | Vulture |")
    print("|--------|-------------:|-------------:|------------------------------:|--------:|")
    print(f"| True Positives  | {len(s_tp)} | {len(h_tp)} | {len(a_tp)} | {len(v_tp)} |")
    print(f"| False Positives | {len(s_fp)} | {len(h_fp)} | {len(a_fp)} | {len(v_fp)} |")
    print(f"| False Negatives | {len(s_fn)} | {len(h_fn)} | {len(a_fn)} | {len(v_fn)} |")
    print(f"| Precision       | {s_prec:.1f}% | {h_prec:.1f}% | {a_prec:.1f}% | {v_prec:.1f}% |")
    print(f"| Recall          | {s_rec:.1f}% | {h_rec:.1f}% | {a_rec:.1f}% | {v_rec:.1f}% |")
    print(f"| **Speed**       | **{t_static:.3f}s** | **{t_hybrid:.3f}s** | *(same run)* | {t_vulture:.3f}s |")

    static_tps = s_static_set & expected_set
    confirmed_tps = static_tps & s_agree_set
    missed_tps = static_tps - s_agree_set

    static_fps = s_static_set & used_set
    fps_in_agree = static_fps & s_agree_set
    fps_caught = static_fps - s_agree_set

    llm_new_tps = s_llm_only_set & expected_set
    llm_new_fps = s_llm_only_set & used_set

    print("\n## LLM Impact Analysis\n")

    print("### LLM as Verifier (filtering static results)")
    print(f"- Static true positives confirmed by LLM: {len(confirmed_tps)}/{len(static_tps)}")
    if missed_tps:
        print(f"- Static true positives LLM did NOT confirm: {len(missed_tps)}")
        for f, n in sorted(missed_tps):
            print(f"    ❌ `{f}`: `{n}`")
    if fps_caught:
        print(f"- Static **false positives caught** by LLM (not confirmed): {len(fps_caught)} ✅")
        for f, n in sorted(fps_caught):
            print(f"    ✅ `{f}`: `{n}` — LLM correctly did not confirm this FP")
    if fps_in_agree:
        print(f"- Static false positives LLM ALSO flagged (missed FPs): {len(fps_in_agree)}")
        for f, n in sorted(fps_in_agree):
            print(f"    ❌ `{f}`: `{n}` — LLM also got this wrong")
    if not fps_caught and not fps_in_agree:
        print("- No false positive data to analyze (static had no FPs in ACTUALLY_USED)")

    print()
    print("### LLM as Discovery (finding dead code static missed)")
    print(f"- LLM-only findings total: {len(s_llm_only_set)}")
    if llm_new_tps:
        print(f"- LLM-only true positives (new discoveries): {len(llm_new_tps)} ✅")
        for f, n in sorted(llm_new_tps):
            print(f"    ✅ `{f}`: `{n}`")
    else:
        print("- LLM-only true positives: 0 (no new dead code found beyond static)")
    if llm_new_fps:
        print(f"- LLM-only false positives: {len(llm_new_fps)}")
        for f, n in sorted(llm_new_fps):
            print(f"    ❌ `{f}`: `{n}`")

    print()
    print("### Net Value of High-Confidence Subset (static∩llm)")
    if len(a_fp) < len(s_fp):
        print(f"- Precision improvement: {s_prec:.1f}% → {a_prec:.1f}% "
              f"(eliminated {len(s_fp) - len(a_fp)} false positive(s))")
    elif len(a_fp) == len(s_fp):
        print(f"- No precision improvement (same FP count: {len(a_fp)})")
    else:
        print(f"- Precision regressed: {s_prec:.1f}% → {a_prec:.1f}%")

    recall_loss = len(s_tp) - len(a_tp)
    if recall_loss > 0:
        print(f"- Recall cost: lost {recall_loss} true positive(s) "
              f"({s_rec:.1f}% → {a_rec:.1f}%)")
    else:
        print(f"- No recall cost (same TP count)")

    print("\n## Detailed Comparison (Expected Unused)\n")
    print("| Item | Static | Hybrid | High-Conf | Vulture | LLM Confirmed? |")
    print("|------|--------|--------|-----------|---------|----------------|")
    for file, name, _cat in expected:
        key = (file, name)
        ss = "✅" if key in s_static_set else "❌"
        sh = "✅" if key in s_hybrid_set else "❌"
        sa = "✅" if key in s_agree_set else "❌"
        vv = "✅" if key in v_set else "❌"
        ag = "✅" if key in s_agree_set else ("🔍 llm-only" if key in s_llm_only_set else "❌")
        print(f"| `{file}`: `{name}` | {ss} | {sh} | {sa} | {vv} | {ag} |")

    print("\n## False Positives (Should NOT be flagged)\n")
    print("| Item | Static | Hybrid | High-Conf | Vulture |")
    print("|------|--------|--------|-----------|---------|")
    any_fp = False
    for file, name in ACTUALLY_USED:
        key = (file, name)
        ss = "❌ FP" if key in s_static_set else "✅"
        sh = "❌ FP" if key in s_hybrid_set else "✅"
        sa = "❌ FP" if key in s_agree_set else "✅"
        vv = "❌ FP" if key in v_set else "✅"
        if ss != "✅" or sh != "✅" or sa != "✅" or vv != "✅":
            print(f"| `{file}`: `{name}` | {ss} | {sh} | {sa} | {vv} |")
            any_fp = True
    if not any_fp:
        print("| *(none)* | — | — | — | — |")

    if missed_tps:
        underscore_misses = [(f, n) for f, n in missed_tps if n.startswith("_")]
        non_underscore_misses = [(f, n) for f, n in missed_tps if not n.startswith("_")]
        all_expected_underscore = [(f, n) for f, n, _ in expected if n.startswith("_")]
        all_expected_non_underscore = [(f, n) for f, n, _ in expected if not n.startswith("_")]

        print("\n## LLM Disagreement Bias Analysis\n")
        print(f"- LLM missed {len(underscore_misses)}/{len(all_expected_underscore)} "
              f"underscore-prefixed items "
              f"({len(underscore_misses)/max(1,len(all_expected_underscore))*100:.0f}% miss rate)")
        print(f"- LLM missed {len(non_underscore_misses)}/{len(all_expected_non_underscore)} "
              f"non-underscore items "
              f"({len(non_underscore_misses)/max(1,len(all_expected_non_underscore))*100:.0f}% miss rate)")
        if len(underscore_misses) > len(non_underscore_misses):
            print("- ⚠️  **Underscore-prefix bias detected**: LLM is more likely to "
                  "mark `_`-prefixed dead code as alive (likely speculating about "
                  "dynamic dispatch without evidence)")

    if llm_new_tps:
        print("\n## LLM-only Suggestions that match Expected Unused (extra credit)\n")
        for file, name in sorted(llm_new_tps):
            print(f"- `{file}`: `{name}`")

    dfp_set = {(f, n) for f, n in DYNAMIC_FALSE_POSITIVES}

    s_dfp_flagged = s_static_set & dfp_set  # static incorrectly flagged these
    h_dfp_flagged = s_hybrid_set & dfp_set  # hybrid incorrectly flagged these
    a_dfp_flagged = s_agree_set & dfp_set  # high-conf incorrectly flagged these
    v_dfp_flagged = v_set & dfp_set  # vulture incorrectly flagged these

    print("\n## Dynamic Dispatch FP Traps (should NOT be flagged)\n")
    print("These are used via getattr(), globals(), or __init_subclass__ — static can't see the references.\n")
    print("| Item | Mechanism | Static | Hybrid | High-Conf | Vulture |")
    print("|------|-----------|--------|--------|-----------|---------|")
    mechanisms = {
        "export_csv": "getattr()", "export_json": "getattr()", "export_xml": "getattr()",
        "handle_create": "globals()", "handle_update": "globals()", "handle_delete": "globals()",
        "EmailHandler": "__init_subclass__", "SlackAlertHandler": "__init_subclass__",
        "send_welcome_email": "@task registry", "on_note_created_log": "@on() event",
        "on_note_created_notify": "@on() event",
        "_dispatch_email": "getattr()", "_dispatch_slack": "getattr()", "_dispatch_sms": "getattr()",
    }
    for file, name in DYNAMIC_FALSE_POSITIVES:
        key = (file, name)
        ss = "❌ FP" if key in s_static_set else "✅"
        sh = "❌ FP" if key in s_hybrid_set else "✅ Caught"
        sa = "❌ FP" if key in s_agree_set else "✅ Caught"
        vv = "❌ FP" if key in v_set else "✅"
        mech = mechanisms.get(name, "?")
        print(f"| `{file}`: `{name}` | {mech} | {ss} | {sh} | {sa} | {vv} |")

    print(f"\n**Dynamic FP Score** (lower = better):")
    print(f"- Static: {len(s_dfp_flagged)}/{len(dfp_set)} false positives")
    print(f"- Hybrid: {len(h_dfp_flagged)}/{len(dfp_set)} false positives")
    print(f"- High-Conf: {len(a_dfp_flagged)}/{len(dfp_set)} false positives")
    print(f"- Vulture: {len(v_dfp_flagged)}/{len(dfp_set)} false positives")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Benchmark Skylos dead-code detection (Static + Hybrid LLM mode)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default (confidence=10)
  python benchmark_hybrid.py

  # Test with different confidence levels
  python benchmark_hybrid.py --confidence 10
  python benchmark_hybrid.py --confidence 20
  python benchmark_hybrid.py --confidence 60

  # Skip LLM verification (static-only benchmark)
  python benchmark_hybrid.py --no-llm
        """
    )
    parser.add_argument(
        '--confidence', '-c',
        type=int,
        default=DEFAULT_CONFIDENCE,
        help=f'Confidence threshold for Skylos (default: {DEFAULT_CONFIDENCE})'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM verification (run static-only benchmark)'
    )

    args = parser.parse_args()

    print(f"Running benchmark with confidence={args.confidence}, llm={'disabled' if args.no_llm else 'enabled'}")
    print()

    compare_results(confidence=args.confidence)