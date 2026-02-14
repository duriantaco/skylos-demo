#!/usr/bin/env python3

import subprocess
import json
import re
import time

SKYLOS_CONFIDENCE = 80
EXPECTED_UNUSED = {
    "imports": [
        ("app/logging.py", "math"),
        ("app/api/routers/notes.py", "datetime"),
        ("app/api/deps.py", "get_settings"),
        ("app/api/routers/reports.py", "fmt_money"),
        ("app/integrations/bootstrap.py", "flask"),
        ("app/integrations/bootstrap.py", "sys"),
        ("app/integrations/slack.py", "Tuple")

    ],
    "functions": [
        ("app/config.py", "_is_prod"),
        ("app/api/deps.py", "get_actor_from_headers"),
        ("app/api/routers/notes.py", "_normalize_query"),
        ("app/db/session.py", "_drop_all"),
        ("app/db/crud.py", "_row_to_dict"),
        ("app/services/notes_services.py", "_validate_title"),
        ("app/utils/ids.py", "slugify"),
        ("app/utils/formatters.py", "format_money"),
        ("app/services/payment_services.py", "process"),
        ("app/integrations/http_client.py", "request_text"),
        ("app/integrations/webhook_signing.py", "verify_hmac_sha256_prefixed"),
        ("app/integrations/slack.py", "build_finding_blocks"),
        ("app/integrations/github.py", "find_issue_by_title"),
        ("app/integrations/metrics.py", "timed_request"),

        ("app/services/report_service.py", "_build_header"),
        ("app/services/report_service.py", "_build_footer"),
        ("app/services/report_service.py", "generate_report_v1"),
        ("app/services/report_service.py", "_search_v2"),
    ],
    "variables": [
        ("app/main.py", "APP_DISPLAY_NAME"),
        ("app/db/crud.py", "DEFAULT_PAGE_SIZE"),
        ("app/utils/ids.py", "DEFAULT_REQUEST_ID"),

        ("app/integrations/http_client.py", "DEFAULT_HEADERS"),
        ("app/integrations/metrics.py", "_queue_depth"),
    ],
    "classes": [
        ("app/core/errors.py", "DemoError"),
        ("app/db/models.py", "Tag"),
        ("app/schemas/notes.py", "NoteInternal"),
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
    ("app/utils/ids.py", "new_request_id"),
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
            ["skylos", ".", "--json", "--confidence", str(confidence)],

            capture_output=True,
            text=True,
        )
        end_time = time.perf_counter()
        duration = end_time - start_time
        data = json.loads(result.stdout)
        
        findings = []
        for item in data.get("unused_functions", []):
            findings.append((item.get("file", ""), item.get("simple_name", item.get("name", "")), "functions"))
        for item in data.get("unused_imports", []):
            findings.append((item.get("file", ""), item.get("simple_name", item.get("name", "")), "imports"))
        for item in data.get("unused_variables", []):
            findings.append((item.get("file", ""), item.get("simple_name", item.get("name", "")), "variables"))
        for item in data.get("unused_classes", []):
            findings.append((item.get("file", ""), item.get("simple_name", item.get("name", "")), "classes"))
        
        cwd = os.getcwd()
        normalized = []
        for file, name, cat in findings:
            file = file.replace("\\", "/")
            if file.startswith(cwd):
                file = file[len(cwd):].lstrip("/")
            elif file.startswith("/"):
                if "/app/" in file:
                    file = "app/" + file.split("/app/", 1)[1]
            if file.startswith("./"):
                file = file[2:]
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
            ["vulture", "app/", "--min-confidence", "80"],
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