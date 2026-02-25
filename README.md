## Benchmark: Skylos Dead-Code Detection

This benchmark evaluates **Skylos** dead-code detection on a **polyglot monorepo** containing both Python and TypeScript, with:
- **Two languages**: Python (FastAPI) + TypeScript (Express) with identical architecture
- **150 ground-truth dead-code items**: 110 Python + 40 TypeScript
- **22 dynamic dispatch traps**: 14 Python (getattr, globals, \_\_init\_subclass\_\_, @task registry, @on() events) + 8 TypeScript (bracket notation, Record map, decorators)
- **Fair comparison**: Skylos vs Vulture (Python), Skylos vs Knip (TypeScript)

### Performance Results (Skylos v3.4.3)

#### Python — Static (110 ground truth items, Skylos vs Vulture)

| Metric | Skylos (conf=20) | Skylos (conf=80) | Vulture |
|--------|:----------------:|:----------------:|:-------:|
| **True Positives** | 103 | 72 | 96 |
| **False Positives** | 15 | 15 | 37 |
| **False Negatives** | 7 | 38 | 14 |
| **Precision** | **79.2%** | 76.6% | 55.8% |
| **Recall** | **93.6%** | 65.5% | 87.3% |
| **Speed** | ~2s | ~3.5s | ~0.5s |

#### Python — Hybrid LLM (conf=10, static + LLM verification)

| Metric | Static | Hybrid | High-Conf (static∩llm) | Vulture |
|--------|:------:|:------:|:----------------------:|:-------:|
| **True Positives** | 103 | 102 | 102 | 96 |
| **False Positives** | 15 | 15 | **13** | 37 |
| **False Negatives** | 7 | 8 | 8 | 14 |
| **Precision** | 79.2% | 76.7% | **78.5%** | 55.8% |
| **Recall** | **93.6%** | 92.7% | 92.7% | 87.3% |
| **Speed** | ~1.2s | ~443s | *(same run)* | ~0.3s |

#### TypeScript (40 ground truth items, Skylos vs Knip)

| Metric | Skylos (conf=20) | Skylos (conf=80) | Knip |
|--------|:----------------:|:----------------:|:----:|
| **True Positives** | 34 | 34 | 31 |
| **False Positives** | 3 | 3 | 14 |
| **False Negatives** | 6 | 6 | 9 |
| **Precision** | **81.0%** | **81.0%** | 72.1% |
| **Recall** | **85.0%** | **85.0%** | 77.5% |
| **Speed** | ~25s | ~11s | ~4s |

**Key takeaways:**
- **Python conf=20** is the sweet spot: +23.4% precision over Vulture, +6.3% recall, and 60% fewer false positives (15 vs 37)
- **Hybrid High-Conf** eliminates 2 more FPs (15 → 13) with minimal recall cost (93.6% → 92.7%)
- **Dynamic dispatch**: Skylos v3.4.3 catches all 14 Python dynamic dispatch patterns in static mode (0/14 FPs vs Vulture's 14/14 FPs)
- **TypeScript**: Skylos has +8.9% precision and +7.5% recall over Knip, with 78% fewer false positives (3 vs 14)
- TS confidence threshold has no effect (all TS findings are high-confidence)

## What are we measuring?

We're measuring **dead-code detection quality** at different **confidence thresholds**.

The Python side includes enterprise patterns: middleware, decorators, ABC/strategy, background tasks, caching, feature flags, custom exceptions, events, pagination, auth, plugins, tests, notifications, and audit — totaling 110 dead-code items across 55 Python files.

### Confidence Thresholds

- **conf=20** (balanced): Filters out very-low-confidence findings
- **conf=80** (conservative): Only high-confidence findings (minimizes false positives)

### True Positives (TP)
Items in `EXPECTED_UNUSED` that the tool flags as unused.

> “Correctly found dead code.”

### False Negatives (FN)
Items in `EXPECTED_UNUSED` that the tool **misses**.

> “Dead code that the tool failed to detect.”

### False Positives (FP)
Items in `ACTUALLY_USED` that the tool flags as unused.

> “Noise: things that are actually used but the tool says are dead.”

### Precision
How often a tool’s reported dead-code findings are correct.

- `precision = TP / (TP + FP)`

High precision = fewer false alarms.

### Recall
How much of the known dead code the tool successfully finds.

- `recall = TP / (TP + FN)`

High recall = misses less dead code.

---

## Running the Benchmark

### Prerequisites
```bash
# Install Skylos
pip install skylos

# Install comparison tools
pip install vulture
npm install -g knip  # or: cd web && npm install && cd ..
```

### Reproducing the Results

```bash
git clone <repo-url>
cd skylos-demo
pip install skylos vulture
cd web && npm install && cd ..

# Python static benchmark (Skylos vs Vulture, conf=20)
python benchmark.py

# Python hybrid benchmark (Skylos static + LLM vs Vulture, conf=10)
export OPENAI_API_KEY=your_key_here  # or any litellm-supported provider
python benchmark_hybrid.py

# TypeScript benchmark (Skylos vs Knip, conf=80)
python benchmark_ts.py
```

To test at different confidence levels, change `SKYLOS_CONFIDENCE` at the top of each script.

---

## Analysis: The Dynamic Dispatch Problem

Static analysis traditionally struggles with patterns where functions are called dynamically at runtime. Vulture and Knip generate false positives on all such patterns. Skylos v3.4.3 handles them natively in static mode (0/14 Python FPs, 0/8 TypeScript FPs).

**getattr() dispatch:**
```python
def export_csv(data): ...  # Static sees 0 references
def run_export(fmt):
    handler = getattr(sys.modules[__name__], f"export_{fmt}")
    return handler(data)
```

**globals() dict access:**
```python
def handle_create(payload): ...  # Static sees 0 references
HANDLER_MAP = {action: globals()[f"handle_{action}"] for action in ("create", "update", "delete")}
```

**__init_subclass__ registration:**
```python
class Base:
    def __init_subclass__(cls):
        REGISTRY[cls.name] = cls
class EmailHandler(Base):  # registered at import time
    name = "email"
```

This benchmark includes 22 such traps (14 Python + 8 TypeScript). Skylos correctly avoids false-flagging all of them; Vulture flags all 14 Python patterns as dead code.

---

## What we are doing

1. **Define ground truth**
   - `EXPECTED_UNUSED`: a curated list of symbols that are *truly unused* in the repo.
     - Includes unused imports, helper functions, constants, and unused classes/schemas/models.
   - `ACTUALLY_USED`: a curated list of symbols that are *definitely used* (should not be flagged).

2. **Run both tools**
   - Run Skylos with JSON output (and a confidence threshold).
   - Run Vulture with a min-confidence threshold.

3. **Normalize outputs**
   - Convert paths to consistent relative paths (e.g. `app/...`).
   - Normalize symbol names where tools disagree on representation (e.g. alias imports).
     - Example: `from x import format_money as fmt_money` may be reported as either `fmt_money` or `format_money` depending on tool. We canonicalize them so comparison is fair.

4. **Compute correctness**
   - Convert each tool’s output into a set of `(file, symbol)` pairs.
   - Compare those sets to ground truth sets.

5. **Print summary + detailed tables**
   - A summary table of TP/FP/FN + precision/recall.
   - A per-ground-truth checklist of what each tool found/missed.
   - Any false positives (things marked used but flagged).
   - Any “other” findings not in either list.

---

## What is being tested (and why we think it's realistic)

This repo is structured like a real polyglot monorepo with two apps:

- **Python** (`app/`): FastAPI app with SQLAlchemy, Pydantic, and httpx integrations
- **TypeScript** (`web/`): Express app mirroring the same architecture with TS-specific patterns

Both apps share the same layered architecture: routes -> services -> db/crud/models -> schemas, with:
- helper functions that are left around but never called
- unused imports after refactors
- unused schemas/models from feature churn
- integration code (webhooks, slack/github clients) with a mix of used + unused helpers

We are explicitly testing:

### 1) Basic dead-code detection
- Unused imports (14 items: 8 Python + 6 TypeScript)
- Unused private helpers (`_normalize_query`/`_normalizeQuery`, `_row_to_dict`/`_rowToObject`, `_build_search_query`, etc.)
- Unused constants (`DEFAULT_PAGE_SIZE`, `APP_DISPLAY_NAME`, `MAX_UPLOAD_SIZE`, `AUDIT_RETENTION_DAYS`, etc.)
- Unused classes, interfaces, and schemas (`DemoError`, `Tag`, `NoteInternal`, `NotePatch`, `Comment`, `Attachment`, etc.)

**Why it matters:** This is the bread-and-butter of dead-code tools.

**Expected behavior:**
- Static analysis should catch most of these (high recall)
- These are straightforward cases with no ambiguity

### 2) Cross-file dependency usage
Symbols that are defined in one layer but used in another:
- routers call service functions
- services call CRUD functions
- CRUD uses models / sessions

**Why it matters:** Real dead-code analysis is mostly about cross-file reference tracking.

**Expected behavior:**
- Tools must build full project call graph, not just per-file analysis
- Failure mode: marking used functions as dead due to incomplete reference tracking

### 3) Framework "implicit usage" (FastAPI wiring)
FastAPI endpoints can be "used" even if nothing directly calls them:
- `@router.get(...)` handlers are invoked by the framework at runtime
- router objects become active when included via `include_router(...)`

**Why it matters:** Many dead-code tools struggle here and produce false positives (noise).

**Expected behavior:**
- Tools should recognize `@router.get/post/...` as framework registration
- Tools should recognize `app.include_router()` makes routers "used"
- Failure mode: flagging active endpoints as unused

### 4) **Dynamic dispatch patterns**

#### Python (14 test cases)

**Pattern 4a: getattr() dispatch** (6 test cases — export\_service + notification\_service)
```python
def export_csv(data): ...  # 0 static references
def export_json(data): ...  # 0 static references

def run_export(fmt):
    handler = getattr(sys.modules[__name__], f"export_{fmt}")
    return handler(data)  # called dynamically
```

**Pattern 4b: globals() dict access** (3 test cases)
```python
def handle_create(payload): ...  # 0 static references

HANDLER_MAP = {
    action: globals()[f"handle_{action}"]
    for action in ("create", "update", "delete")
}
```

**Pattern 4c: __init_subclass__ registration** (2 test cases)
```python
class RegisteredHandler:
    def __init_subclass__(cls):
        REGISTRY[cls.name] = cls

class EmailHandler(RegisteredHandler):
    name = "email"
```

**Pattern 4d: @task decorator registry** (1 test case)
```python
@task("send_welcome_email")
def send_welcome_email(email=""):  # registered via decorator
    print(f"Sending welcome email to {email}")
```

**Pattern 4e: @on() event handler registration** (2 test cases)
```python
@EventBus.on("note_created")
def on_note_created_log(**kwargs):  # called via EventBus.emit()
    print(f"note_created: {kwargs.get('title')}")
```

#### TypeScript (8 test cases)

**Pattern 4d: Bracket notation on module exports** (3 test cases)
```typescript
export function exportCsv(data: unknown[]): string { ... }
export function exportJson(data: unknown[]): string { ... }

import * as self from "./exportService";
export function runExport(data: unknown[], fmt: string): string {
  const handler = (self as Record<string, unknown>)[handlerName];
  return handler(data);  // called dynamically
}
```

**Pattern 4e: Record<string, Function> map** (3 test cases)
```typescript
export function handleCreate(payload): Record<string, unknown> { ... }

const HANDLER_MAP: Record<string, Function> = {
  create: handleCreate, update: handleUpdate, delete: handleDelete,
};
```

**Pattern 4f: Decorator-based registry** (2 test cases)
```typescript
@RegisterHandler("email")
export class EmailHandler extends RegisteredHandler { ... }
```

**Why it matters:** Static analysis sees 0 references → flags as dead (false positive). Dynamic dispatch is common in both Python and TypeScript codebases.

**Expected behavior:**
- **Vulture/Knip**: Flag all dynamic patterns as dead (false positives)
- **Skylos v3.4.3**: Correctly identifies all 22 as used (0 false positives)

### 5) Name-collision / heuristic traps
A deliberate example where method names collide (e.g. `process` exists on multiple classes):
- `CreditCard.process()` is used
- `PayPal.process()` is NOT used (but has same name)

**Why it matters:** Naive approaches may overgeneralize "method name is used somewhere ⇒ all methods with that name are used".

**Expected behavior:**
- Tools should distinguish between different class methods with same name
- Failure mode: marking `PayPal.process` as used due to `CreditCard.process` usage

### 6) Transitive dead code (HARD - not yet caught)

Functions only called by other dead functions:
```python
def _build_header(title): ...
def generate_report_v1(...):     # 0 references
    header = _build_header(...) 
```

**Why it matters:** Helps find "chains" of dead code where helper functions are only used by unused code.

**Expected behavior:**
- **Current state:** No tool catches this (requires graph-based propagation)
- **Future work:** Need transitive dead code analysis in static analyzer

**Current false negatives:**
- `_build_header` (only called by dead `generate_report_v1`)
- `_build_footer` (only called by dead `generate_report_v1`)

### 7) Alias-import reporting differences
Imports like `import x as y` can be represented differently by different tools.
We normalize this so we are measuring detection quality, not string formatting.

---

## Why we think this is a good test

This benchmark is "good" because it is:

### Ground truthed
We don't just eyeball outputs; we compare against a known list of unused and used items (150 expected unused across 2 languages, 141 actually used).

### Mixed difficulty
It contains:
- **Easy cases** (unused import, unused constant)
- **Medium cases** (unused helper in a services layer, cross-file references)
- **Hard cases** (framework wiring, alias imports, name collisions)
- **Very hard cases** (dynamic dispatch patterns that fool static analysis)

The **dynamic dispatch patterns** (22 test cases across Python + TypeScript) are the key differentiator that tests whether tools can handle real-world polyglot patterns.

### Multi-language
Tests that the tool works across Python and TypeScript with equivalent detection quality. Vulture is Python-only and serves as a single-language baseline.

### Fair comparison
We normalize tool outputs to avoid penalizing one tool for naming conventions (e.g. alias reporting).

### Actionable
The outputs directly map to:
- what the tool should catch (true positives)
- what it missed (false negatives)
- what it incorrectly flagged (false positives)

### Tests advanced features
The dynamic dispatch patterns (22 test cases) specifically test how well tools handle real-world patterns that fool naive static analysis.

---

## When this benchmark would NOT be "good" (and what we'd change down the line)

To keep this benchmark credible, we must ensure:

### A) Ground truth stays correct
If `EXPECTED_UNUSED` contains items that are actually used internally (e.g. dataclasses instantiated within their own module), then we inflate false negatives and distort recall.
**Fix:** only include truly unused items.

### B) ACTUALLY_USED is truly used
If `ACTUALLY_USED` includes things that are not actually referenced anywhere (e.g. a helper that isn’t imported/called), then we inflate false positives and distort precision.
**Fix:** only list items with a real call-site/import path.

### C) We do not count non-app files unintentionally
If the tool scans `benchmark.py` itself, "Other Findings" will include benchmark helpers and dilute the demo.
**Fix:** run tools on `app/` and `tests/` only.

### D) We will evolve the test as Skylos improves
Once Skylos handles these patterns well, we can add additional realistic scenarios:
- dynamically imported plugins (entrypoints / registries)
- pydantic validators and model config usage
- FastAPI dependencies (`Depends(...)`) used via injection
- conditional imports / typing-only imports

---

## Summary

This benchmark evaluates Skylos dead-code detection by:
- **Testing across Python + TypeScript** with identical architecture and dead-code categories
- **Testing 22 dynamic dispatch patterns** across both languages that fool static analysis
- **Measuring TP/FP/FN** against curated ground truth (150 expected unused, 141 actually used)
- **Comparing against Vulture** (Python-only) and **Knip** (TypeScript-only)
- **Reporting precision/recall** plus detailed per-item results

### Key Findings

1. **Python**: Skylos has +23.4% precision over Vulture (79.2% vs 55.8%) and +6.3% recall (93.6% vs 87.3%) at conf=20
2. **Dynamic dispatch**: Skylos v3.4.3 catches all 14 Python dynamic patterns in static mode (Vulture: 14/14 false positives)
3. **TypeScript**: Skylos has +8.9% precision and +7.5% recall over Knip, with 78% fewer false positives (3 vs 14)
4. **Hybrid LLM**: Eliminates 2 additional FPs with minimal recall cost (93.6% → 92.7%)


## Expected Skylos Findings (Demo)

This repo intentionally contains unused imports / functions / variables / classes so Skylos has something to detect.

> **Warning:** The security issues below are intentionally unsafe for benchmarking. Do **NOT** deploy this repo.

### Unused Imports

**Python (8)**
- `app/logging.py`: `import math`
- `app/api/routers/notes.py`: `from datetime import datetime`
- `app/api/deps.py`: `from app.config import get_settings`
- `app/api/deps.py`: `Session`
- `app/api/routers/reports.py`: `from app.utils.formatters import format_money as fmt_money`
- `app/integrations/bootstrap.py`: `flask`
- `app/integrations/bootstrap.py`: `sys`
- `app/integrations/slack.py`: `Tuple`

**TypeScript (6)**
- `web/src/logging.ts`: `import path`
- `web/src/routes/notes.ts`: `import { URL }`
- `web/src/middleware/auth.ts`: `import { loadConfig }`
- `web/src/routes/reports.ts`: `import { formatMoney }`
- `web/src/integrations/bootstrap.ts`: `import express`
- `web/src/integrations/slack.ts`: `import { EventEmitter }`

### Unused Functions

**Python (63)**
- `app/config.py`: `_is_prod()`, `_parse_cors_origins()`
- `app/api/deps.py`: `get_actor_from_headers()`
- `app/api/routers/notes.py`: `_normalize_query()`
- `app/api/routers/reports.py`: `generate_report()`
- `app/db/session.py`: `_drop_all()`, `get_engine_info()`, `_reset_sequences()`
- `app/db/crud.py`: `_row_to_dict()`, `bulk_create_notes()`, `_build_search_query()`
- `app/services/notes_services.py`: `_validate_title()`, `normalize_and_score_query()`
- `app/utils/ids.py`: `slugify()`, `new_request_id()`, `weak_token()`
- `app/utils/formatters.py`: `format_money()`
- `app/services/payment_services.py`: `process()`, `run_payment()` (method-name collision trap)
- `app/core/errors.py`: `not_found()`
- `app/integrations/http_client.py`: `request_text()`
- `app/integrations/webhook_signing.py`: `verify_hmac_sha256_prefixed()`
- `app/integrations/slack.py`: `build_finding_blocks()`
- `app/integrations/github.py`: `find_issue_by_title()`
- `app/integrations/metrics.py`: `timed_request()`, `snapshot_metrics()`, `add_tags()`
- `app/services/report_service.py`: `_build_header()`, `_build_footer()`, `generate_report_v1()`, `_search_v2()`
- `app/core/middleware.py`: `generate_correlation_id()`
- `app/core/decorators.py`: `validate_input()`, `deprecate()`
- `app/services/tasks.py`: `generate_daily_report()`, `sync_external_contacts()`, `cleanup_expired_sessions()`
- `app/core/cache.py`: `invalidate_cache_for()`
- `app/core/feature_flags.py`: `get_all_flags()`, `_evaluate_flag_with_context()`
- `app/core/events.py`: `on_note_deleted_cleanup()`, `on_user_signed_up_welcome()`
- `app/core/pagination.py`: `apply_filters()`
- `app/core/auth.py`: `validate_bearer_token()`, `generate_api_token()`, `check_ip_allowlist()`
- `app/core/plugins.py`: `list_plugins()`, `unload_plugin()`
- `app/services/notification_service.py`: `send_bulk_notifications()`, `schedule_notification()`, `_render_template()`
- `app/services/audit_service.py`: `query_audit_log()`, `_redact_sensitive_fields()`, `export_audit_csv()`
- `tests/conftest.py`: `mock_redis()`, `admin_user()`
- `tests/factories.py`: `random_email()`
- `tests/helpers.py`: `assert_paginated_response()`, `wait_for_event()`, `mock_external_service()`
- `tests/test_notes.py`: `test_create_note_with_tags()`, `test_bulk_import_notes()`, `_seed_notes()`

**TypeScript (23)**
- `web/src/config.ts`: `_isProd()`
- `web/src/middleware/auth.ts`: `getActorFromHeaders()`
- `web/src/routes/notes.ts`: `_normalizeQuery()`
- `web/src/db/session.ts`: `_dropAll()`
- `web/src/db/crud.ts`: `_rowToObject()`
- `web/src/services/noteService.ts`: `_validateTitle()`
- `web/src/utils/ids.ts`: `slugify()`
- `web/src/utils/formatters.ts`: `formatMoney()`
- `web/src/services/paymentService.ts`: `process` (same-name method trap), `runPayment()`
- `web/src/core/errors.ts`: `notFound()`
- `web/src/integrations/httpClient.ts`: `requestText()`, `getHttpClient()`
- `web/src/integrations/webhookSigning.ts`: `verifyHmacSha256Prefixed()`
- `web/src/integrations/slack.ts`: `buildFindingBlocks()`
- `web/src/integrations/github.ts`: `authHeaders()`, `findIssueByTitle()`
- `web/src/integrations/metrics.ts`: `snapshotMetrics()`, `timedRequest()`
- `web/src/services/reportService.ts`: `_buildHeader()`, `_buildFooter()`, `generateReportV1()`, `_searchV2()`

### Unused Variables / Constants

**Python (17)**
- `app/main.py`: `APP_DISPLAY_NAME`
- `app/config.py`: `MAX_UPLOAD_SIZE`
- `app/db/crud.py`: `DEFAULT_PAGE_SIZE`
- `app/db/session.py`: `DB_POOL_SIZE`
- `app/utils/ids.py`: `DEFAULT_REQUEST_ID`
- `app/integrations/http_client.py`: `DEFAULT_HEADERS`
- `app/integrations/metrics.py`: `_queue_depth`
- `app/services/tasks.py`: `TASK_PRIORITY_HIGH`, `TASK_PRIORITY_LOW`
- `app/core/feature_flags.py`: `FLAG_ADMIN_ENDPOINT`
- `app/core/events.py`: `EVENT_NOTE_ARCHIVED`
- `app/core/auth.py`: `ROLE_VIEWER`, `TOKEN_ALGORITHM`
- `app/services/notification_service.py`: `MAX_BATCH_SIZE`
- `app/services/audit_service.py`: `AUDIT_RETENTION_DAYS`
- `tests/conftest.py`: `TEST_TIMEOUT`
- `tests/helpers.py`: `SLOW_TEST_THRESHOLD`

**TypeScript (5)**
- `web/src/index.ts`: `APP_DISPLAY_NAME`
- `web/src/db/crud.ts`: `DEFAULT_PAGE_SIZE`
- `web/src/utils/ids.ts`: `DEFAULT_REQUEST_ID`
- `web/src/integrations/httpClient.ts`: `DEFAULT_HEADERS`
- `web/src/integrations/metrics.ts`: `_queueDepth`

### Unused Classes / Models / Schemas

**Python (22)**
- `app/core/errors.py`: `class DemoError(Exception)`
- `app/db/models.py`: `class Tag(Base)`, `class Comment(Base)`, `class Attachment(Base)`
- `app/schemas/notes.py`: `class NoteInternal(BaseModel)`, `class NotePatch(BaseModel)`, `class NoteSearch(BaseModel)`
- `app/services/payment_services.py`: `class PayPal`
- `app/core/middleware.py`: `class CorrelationIdMiddleware`, `class RateLimitMiddleware`
- `app/core/base.py`: `class MongoNoteRepository`, `class PagerDutyNotifier`
- `app/core/cache.py`: `class RedisCache`
- `app/core/exceptions.py`: `class AuthenticationError`, `class AuthorizationError`, `class RateLimitError`, `class ExternalServiceError`
- `app/core/pagination.py`: `class CursorParams`, `class CursorResult`
- `app/services/notification_service.py`: `class NotificationLog`
- `tests/factories.py`: `class UserFactory`, `class TagFactory`

**TypeScript (6)**
- `web/src/core/errors.ts`: `class DemoError`
- `web/src/db/models.ts`: `interface Tag`
- `web/src/schemas/notes.ts`: `interface NoteInternal`
- `web/src/types/index.ts`: `interface AppConfig`, `interface RequestContext`, `interface PaginationParams`

### Security Findings (Intentionally Vulnerable for Demo)

- `app/db/crud.py`: `search_notes` — **SQL injection** via f-string/interpolated SQL (`text(f"...{q}...")`)
- `app/api/routers/notes.py`: `POST /fetch` (`fetch_url`) — **SSRF-style** untrusted URL fetch via `httpx` client
- `app/api/routers/health.py`: `GET /debug/read-file` (`read_file`) — **Path traversal / arbitrary file read** via `open(path)`
- `app/utils/ids.py`: `weak_token` — **Weak randomness** for tokens (uses `random` instead of `secrets`)


### Quality Findings (Intentionally Bad for Demo)

- `app/integrations/routers/webhook.py`: `POST /integrations/webhooks/demo` (`demo_webhook`) — **Blocking call in async handler** (`time.sleep(0.2)` inside `async def`)
- `app/services/notes_services.py`: `normalize_and_score_query` — **High cyclomatic complexity / deep nesting**
- `app/integrations/metrics.py`: `add_tags` — **Mutable default argument** (`tags: dict = {}`) + mutation
---

### Known Limitations

**Remaining false negatives (7 items Skylos misses at conf=20):**
- 2 event handlers (`on_note_deleted_cleanup`, `on_user_signed_up_welcome`) — registered via `@on()` decorator
- 2 test fixtures (`mock_redis`, `admin_user`) — pytest fixtures not called directly
- 2 test functions (`test_create_note_with_tags`, `test_bulk_import_notes`) — disabled tests
- 1 variable (`MAX_BATCH_SIZE`) — unused constant

**Remaining false positives (15 items Skylos incorrectly flags at conf=20):**
- Cross-file references where the import chain is indirect (e.g. `search`, `dispatch` re-exported via `main.py`)
- Abstract method implementations (`SqlNoteRepository`, `SlackNotifier`, `verify_api_key`)
- Framework-registered items not yet recognized (`ValidationError`, `NotFoundError`)

---

## Citation

If you use this benchmark in your research or tools, please cite:

```
Skylos Dead-Code Detection Benchmark
https://github.com/duriantaco/skylos-demo
Ground-truthed evaluation of static dead code detection
```

