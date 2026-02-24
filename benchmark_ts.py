#!/usr/bin/env python3
import subprocess
import json
import os
import time


SKYLOS_CONFIDENCE = 80

EXPECTED_UNUSED = {
    "imports": [
        ("web/src/logging.ts", "path"),
        ("web/src/routes/notes.ts", "URL"),
        ("web/src/middleware/auth.ts", "loadConfig"),
        ("web/src/routes/reports.ts", "formatMoney"),
        ("web/src/integrations/bootstrap.ts", "express"),
        ("web/src/integrations/slack.ts", "EventEmitter"),
    ],
    "functions": [
        ("web/src/config.ts", "_isProd"),
        ("web/src/middleware/auth.ts", "getActorFromHeaders"),
        ("web/src/routes/notes.ts", "_normalizeQuery"),
        ("web/src/db/session.ts", "_dropAll"),
        ("web/src/db/crud.ts", "_rowToObject"),
        ("web/src/services/noteService.ts", "_validateTitle"),
        ("web/src/utils/ids.ts", "slugify"),
        ("web/src/utils/formatters.ts", "formatMoney"),
        ("web/src/services/paymentService.ts", "process"),
        ("web/src/integrations/httpClient.ts", "requestText"),
        ("web/src/integrations/webhookSigning.ts", "verifyHmacSha256Prefixed"),
        ("web/src/integrations/slack.ts", "buildFindingBlocks"),
        ("web/src/integrations/github.ts", "authHeaders"),
        ("web/src/integrations/github.ts", "findIssueByTitle"),
        ("web/src/integrations/metrics.ts", "snapshotMetrics"),
        ("web/src/integrations/metrics.ts", "timedRequest"),
        ("web/src/integrations/httpClient.ts", "getHttpClient"),
        ("web/src/core/errors.ts", "notFound"),
        ("web/src/services/paymentService.ts", "runPayment"),
        ("web/src/services/reportService.ts", "_buildHeader"),
        ("web/src/services/reportService.ts", "_buildFooter"),
        ("web/src/services/reportService.ts", "generateReportV1"),
        ("web/src/services/reportService.ts", "_searchV2"),
    ],
    "variables": [
        ("web/src/index.ts", "APP_DISPLAY_NAME"),
        ("web/src/db/crud.ts", "DEFAULT_PAGE_SIZE"),
        ("web/src/utils/ids.ts", "DEFAULT_REQUEST_ID"),
        ("web/src/integrations/httpClient.ts", "DEFAULT_HEADERS"),
        ("web/src/integrations/metrics.ts", "_queueDepth"),
    ],
    "classes": [
        ("web/src/core/errors.ts", "DemoError"),
        ("web/src/db/models.ts", "Tag"),
        ("web/src/schemas/notes.ts", "NoteInternal"),
        ("web/src/types/index.ts", "AppConfig"),
        ("web/src/types/index.ts", "RequestContext"),
        ("web/src/types/index.ts", "PaginationParams"),
    ],
}

ACTUALLY_USED = [
    ("web/src/index.ts", "createApp"),
    ("web/src/index.ts", "app"),
    ("web/src/middleware/auth.ts", "requireApiKey"),
    ("web/src/db/crud.ts", "createNote"),
    ("web/src/db/crud.ts", "listNotes"),
    ("web/src/db/crud.ts", "searchNotes"),
    ("web/src/db/session.ts", "initDb"),
    ("web/src/db/session.ts", "SessionLocal"),
    ("web/src/db/models.ts", "Note"),
    ("web/src/config.ts", "loadConfig"),
    ("web/src/schemas/notes.ts", "NoteCreate"),
    ("web/src/schemas/notes.ts", "NoteOut"),
    ("web/src/services/noteService.ts", "createNoteService"),
    ("web/src/services/noteService.ts", "listNotesService"),
    ("web/src/services/noteService.ts", "searchNotesService"),
    ("web/src/utils/ids.ts", "newRequestId"),
    ("web/src/logging.ts", "configureLogging"),
    ("web/src/routes/health.ts", "healthRouter"),
    ("web/src/routes/notes.ts", "notesRouter"),
    ("web/src/routes/reports.ts", "reportsRouter"),
    ("web/src/routes/index.ts", "healthRouter"),
    ("web/src/routes/index.ts", "notesRouter"),
    ("web/src/routes/index.ts", "reportsRouter"),
    ("web/src/integrations/bootstrap.ts", "initIntegrations"),
    ("web/src/integrations/routes/webhooks.ts", "webhooksRouter"),
    ("web/src/integrations/webhookSigning.ts", "verifyHmacSha256"),
    ("web/src/integrations/metrics.ts", "recordRequest"),
    ("web/src/integrations/metrics.ts", "recordLatencyMs"),
    ("web/src/services/exportService.ts", "runExport"),
    ("web/src/services/exportService.ts", "exportCsv"),
    ("web/src/services/exportService.ts", "exportJson"),
    ("web/src/services/exportService.ts", "exportXml"),
    ("web/src/handlers/index.ts", "dispatch"),
    ("web/src/handlers/index.ts", "handleCreate"),
    ("web/src/handlers/index.ts", "handleUpdate"),
    ("web/src/handlers/index.ts", "handleDelete"),
    ("web/src/core/registry.ts", "getHandler"),
    ("web/src/core/registry.ts", "EmailHandler"),
    ("web/src/core/registry.ts", "SlackAlertHandler"),
    ("web/src/services/reportService.ts", "search"),
    ("web/src/integrations/slack.ts", "sendSlackMessage"),
    ("web/src/integrations/httpClient.ts", "requestJson"),
    ("web/src/integrations/github.ts", "getRepo"),
    ("web/src/integrations/routes/webhooks.ts", "demoWebhook"),
    ("web/src/utils/formatters.ts", "formatDate"),
    ("web/src/integrations/webhookSigning.ts", "signHmacSha256"),
    ("web/src/core/registry.ts", "RegisterHandler"),
    ("web/src/config.ts", "Settings"),
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


def run_skylos(confidence=SKYLOS_CONFIDENCE):
    start = time.perf_counter()
    try:
        result = subprocess.run(
            ["skylos", "web/", "--json", "--confidence", str(confidence)],
            capture_output=True,
            text=True,
        )
        dur = time.perf_counter() - start
        data = json.loads(result.stdout)

        findings = []
        for cat_key, cat_name in [
            ("unused_functions", "functions"),
            ("unused_imports", "imports"),
            ("unused_variables", "variables"),
            ("unused_classes", "classes"),
        ]:
            for item in data.get(cat_key, []):
                file = _relativize(item.get("file", ""))
                name = item.get("simple_name") or item.get("name") or ""
                if "." in name and "/" not in name and not name.startswith("_"):
                    name = name.split(".")[-1]
                if file.startswith("web/src/"):
                    findings.append((file, name, cat_name))

        return findings, dur
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
            cwd=os.path.join(os.getcwd(), "web"),
        )
        dur = time.perf_counter() - start
        data = json.loads(result.stdout)

        findings = []

        for file_path in data.get("files", []):
            norm = "web/" + file_path.replace("\\", "/")
            findings.append((norm, "*FILE*", "files"))

        for issue in data.get("issues", []):
            file_path = "web/" + issue.get("file", "").replace("\\", "/")
            for item in issue.get("exports", []):
                findings.append((file_path, item["name"], "functions"))
            for item in issue.get("types", []):
                findings.append((file_path, item["name"], "classes"))
            for members in issue.get("classMembers", {}).values():
                for item in members:
                    findings.append((file_path, item["name"], "functions"))

        return findings, dur
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


def compare_results():
    expected = get_all_expected()
    expected_set = {(f, n) for f, n, _ in expected}
    used_set = {(f, n) for f, n in ACTUALLY_USED}

    skylos_findings, skylos_time = run_skylos()
    knip_findings, knip_time = run_knip()

    skylos_set = {(f, n) for f, n, _ in skylos_findings}

    knip_direct = {(f, n) for f, n, _ in knip_findings if n != "*FILE*"}
    knip_dead_files = {f for f, n, _ in knip_findings if n == "*FILE*"}

    # Skylos metrics
    s_tp = skylos_set & expected_set
    s_fp = skylos_set & used_set
    s_fn = expected_set - skylos_set

    # Knip metrics
    k_tp = set()
    k_fp = set()
    k_fn = set()
    for f, n in expected_set:
        if (f, n) in knip_direct or f in knip_dead_files:
            k_tp.add((f, n))
        else:
            k_fn.add((f, n))
    for f, n in used_set:
        if (f, n) in knip_direct or f in knip_dead_files:
            k_fp.add((f, n))

    knip_total = len(knip_direct) + len(knip_dead_files)

    if skylos_set:
        s_prec = len(s_tp) / len(skylos_set) * 100
    else:
        s_prec = 0

    if expected_set:
        s_rec = len(s_tp) / len(expected_set) * 100
    else:
        s_rec = 0
    
    if knip_total:
        k_prec = len(k_tp) / knip_total * 100
    else:
        k_prec = 0 
    
    if expected_set:
        k_rec = len(k_tp) / len(expected_set) * 100
    else:
        k_rec = 0

    print("\n## Benchmark Results (TypeScript)\n")
    print("| Metric | Skylos | Knip |")
    print("|--------|--------|------|")
    print(f"| True Positives (correctly found) | {len(s_tp)} | {len(k_tp)} |")
    print(f"| False Positives (flagged but used) | {len(s_fp)} | {len(k_fp)} |")
    print(f"| False Negatives (missed) | {len(s_fn)} | {len(k_fn)} |")
    print(f"| Precision | {s_prec:.1f}% | {k_prec:.1f}% |")
    print(f"| Recall | {s_rec:.1f}% | {k_rec:.1f}% |")
    print(f"| **Speed** | **{skylos_time:.4f}s** | {knip_time:.4f}s |")

    print("\n## Detailed Comparison\n")
    print("### Expected Unused (both should find these)\n")
    print("| Item | Skylos | Knip |")
    print("|------|--------|------|")
    for file, name, _cat in expected:
        s = "✅" if (file, name) in skylos_set else "❌"
        k = "✅" if _match_knip(knip_findings, file, name) else "❌"
        print(f"| `{file}`: `{name}` | {s} | {k} |")

    print("\n### False Positives (should NOT be flagged)\n")
    print("| Item | Skylos | Knip |")
    print("|------|--------|------|")
    any_fp = False
    for file, name in ACTUALLY_USED:
        s_flag = "❌ FP" if (file, name) in skylos_set else "✅"
        k_flag = "❌ FP" if _match_knip(knip_findings, file, name) else "✅"
        if s_flag != "✅" or k_flag != "✅":
            print(f"| `{file}`: `{name}` | {s_flag} | {k_flag} |")
            any_fp = True
    if not any_fp:
        print("| *(none)* | — | — |")

    if knip_dead_files:
        print("\n### Knip: Entirely Unused Files\n")
        for f in sorted(knip_dead_files):
            print(f"- `{f}`")

    print("\n### Other Findings (not in ground truth)\n")
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
        print("None")


if __name__ == "__main__":
    compare_results()
