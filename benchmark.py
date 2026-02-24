#!/usr/bin/env python3

import subprocess
import json
import re
import time

SKYLOS_CONFIDENCE = 20
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


def run_skylos(confidence=SKYLOS_CONFIDENCE):
    import os

    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            ["skylos", "app/", "tests/", "--json", "--confidence", str(confidence)],
            capture_output=True,
            text=True,
        )
        end_time = time.perf_counter()
        duration = end_time - start_time
        data = json.loads(result.stdout)

        findings = []
        for item in data.get("unused_functions", []):
            findings.append(
                (item.get("file", ""), item.get("simple_name", item.get("name", "")), "functions")
            )
        for item in data.get("unused_imports", []):
            findings.append(
                (item.get("file", ""), item.get("simple_name", item.get("name", "")), "imports")
            )
        for item in data.get("unused_variables", []):
            findings.append(
                (item.get("file", ""), item.get("simple_name", item.get("name", "")), "variables")
            )
        for item in data.get("unused_classes", []):
            findings.append(
                (item.get("file", ""), item.get("simple_name", item.get("name", "")), "classes")
            )

        cwd = os.getcwd()
        normalized = []
        for file, name, cat in findings:
            file = file.replace("\\", "/")
            if file.startswith(cwd):
                file = file[len(cwd) :].lstrip("/")
            elif file.startswith("/"):
                if "/app/" in file:
                    file = "app/" + file.split("/app/", 1)[1]
            if file.startswith("./"):
                file = file[2:]
            if not file.startswith("app/") and not file.startswith("tests/"):
                continue
            if "." in name and "/" not in name and not name.startswith("_"):
                name = name.split(".")[-1]
            file, name = canonicalize(file, name)
            normalized.append((file, name, cat))

        return normalized, duration
    except Exception as e:
        print(f"Skylos error: {e}")
        return []


def run_vulture():
    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            ["vulture", "app/", "tests/", "--min-confidence", "20"],
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
                kind = match.group(3)  # function, variable, import, class
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
        return []


def normalize_finding(file, name):
    file = file.replace("\\", "/")
    if file.startswith("./"):
        file = file[2:]
    return (file, name)


def canonicalize(file: str, name: str) -> tuple[str, str]:
    file = file.replace("\\", "/")
    if file.startswith("./"):
        file = file[2:]

    if file == "app/api/routers/reports.py":
        if name == "format_money":
            name = "fmt_money"

    return file, name


def compare_results():
    expected = get_all_expected()
    expected_set = {(f, n) for f, n, _ in expected}
    used_set = {(f, n) for f, n in ACTUALLY_USED}

    skylos_findings, skylos_time = run_skylos()
    vulture_findings, vulture_time = run_vulture()

    skylos_set = {(f, n) for f, n, _ in skylos_findings}
    vulture_set = {(f, n) for f, n, _ in vulture_findings}

    skylos_tp = skylos_set & expected_set
    skylos_fp = skylos_set & used_set
    skylos_fn = expected_set - skylos_set

    vulture_tp = vulture_set & expected_set
    vulture_fp = vulture_set & used_set
    vulture_fn = expected_set - vulture_set

    print("\n## Benchmark Results\n")
    print("| Metric | Skylos | Vulture |")
    print("|--------|--------|---------|")
    print(f"| True Positives (correctly found) | {len(skylos_tp)} | {len(vulture_tp)} |")
    print(f"| False Positives (flagged but used) | {len(skylos_fp)} | {len(vulture_fp)} |")
    print(f"| False Negatives (missed) | {len(skylos_fn)} | {len(vulture_fn)} |")

    total_expected = len(expected_set)
    skylos_precision = len(skylos_tp) / len(skylos_set) * 100 if skylos_set else 0
    skylos_recall = len(skylos_tp) / total_expected * 100 if total_expected else 0
    vulture_precision = len(vulture_tp) / len(vulture_set) * 100 if vulture_set else 0
    vulture_recall = len(vulture_tp) / total_expected * 100 if total_expected else 0

    print(f"| Precision | {skylos_precision:.1f}% | {vulture_precision:.1f}% |")
    print(f"| Recall | {skylos_recall:.1f}% | {vulture_recall:.1f}% |")
    print(f"| **Speed** | **{skylos_time:.4f}s** | {vulture_time:.4f}s |")

    print("\n## Detailed Comparison\n")

    print("### True Positives (both should find these)\n")
    print("| Item | Skylos | Vulture |")
    print("|------|--------|---------|")
    for file, name, cat in expected:
        s = "✅" if (file, name) in skylos_set else "❌"
        v = "✅" if (file, name) in vulture_set else "❌"
        print(f"| `{file}`: `{name}` | {s} | {v} |")

    print("\n### False Positives (should NOT be flagged)\n")
    print("| Item | Skylos | Vulture |")
    print("|------|--------|---------|")
    for file, name in ACTUALLY_USED:
        s_flag = "❌ FP" if (file, name) in skylos_set else "✅"
        v_flag = "❌ FP" if (file, name) in vulture_set else "✅"
        if s_flag != "✅" or v_flag != "✅":
            print(f"| `{file}`: `{name}` | {s_flag} | {v_flag} |")

    print("\n### Other Findings (not in ground truth)\n")
    all_known = expected_set | used_set
    skylos_other = skylos_set - all_known
    vulture_other = vulture_set - all_known

    if skylos_other or vulture_other:
        print("| Tool | File | Name |")
        print("|------|------|------|")
        for file, name in skylos_other:
            print(f"| Skylos | `{file}` | `{name}` |")
        for file, name in vulture_other:
            print(f"| Vulture | `{file}` | `{name}` |")
    else:
        print("None")


if __name__ == "__main__":
    compare_results()
