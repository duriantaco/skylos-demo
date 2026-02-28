<div align="center">

# Skylos Benchmark Suite

**Manually verified dead-code detection benchmarks across Python, TypeScript, and Go.**

11 real-world repos (370k+ combined stars) + 1 synthetic polyglot monorepo.

Every finding hand-checked against source code. No automated labelling. No cherry-picking.

</div>

---

<div align="center">

### Headline Numbers

| | Skylos | Vulture | Knip |
|:---|:---:|:---:|:---:|
| **Python recall** | **98.1%** | 84.6% | — |
| **TypeScript recall** | **100%** | — | 100% |
| **Python false positives** | **220** | 644 | — |
| **TypeScript precision** | **36.4%** | — | 7.5% |

*9 Python repos (350k+ stars) / 1 TypeScript repo (7k stars)*

</div>

---

## Real-World Repos Tested

| # | Repository | Lang | Stars | What It Stress-Tests |
|---|:---|:---:|---:|:---|
| 1 | [psf/requests](https://github.com/psf/requests) | Python | 53k | `__init__.py` re-exports, Sphinx conf vars, pytest test classes |
| 2 | [pallets/click](https://github.com/pallets/click) | Python | 17k | IO protocol methods (`io.RawIOBase` subclasses), nonlocal closures |
| 3 | [encode/starlette](https://github.com/encode/starlette) | Python | 10k | ASGI interface params, polymorphic dispatch, public API surface |
| 4 | [Textualize/rich](https://github.com/Textualize/rich) | Python | 51k | `__rich_console__` protocol, sentinel vars via `f_locals`, metaclasses |
| 5 | [encode/httpx](https://github.com/encode/httpx) | Python | 14k | Transport/auth protocol methods, zero dead code (pure FP stress test) |
| 6 | [pallets/flask](https://github.com/pallets/flask) | Python | 69k | Jinja2 template globals, Werkzeug protocol methods, extension hooks |
| 7 | [pydantic/pydantic](https://github.com/pydantic/pydantic) | Python | 23k | Mypy plugin hooks, hypothesis `@resolves`, `__getattr__` dynamic config |
| 8 | [fastapi/fastapi](https://github.com/fastapi/fastapi) | Python | 82k | 100+ OpenAPI spec model fields (Pydantic BaseModel), Starlette overrides |
| 9 | [tqdm/tqdm](https://github.com/tqdm/tqdm) | Python | 30k | Keras/Dask framework callbacks, Rich column rendering, pandas monkey-patching |
| 10 | [go-chi/chi](https://github.com/go-chi/chi) | Go | 18k | Chained selectors, Go receiver methods, test-file dead code |
| 11 | [unjs/consola](https://github.com/unjs/consola) | TS | 7k | Same-file `as any` casts, orphaned modules, package.json entry points |

Plus a synthetic polyglot monorepo with 150 planted dead-code items across Python + TypeScript.

---

## Results: Python (Skylos vs Vulture)

> Benchmarked on 9 of the most popular Python repos on GitHub — 350k+ combined stars.

| Repository | Dead Items | Skylos TP | Skylos FP | Vulture TP | Vulture FP |
|:---|---:|---:|---:|---:|---:|
| psf/requests | 6 | **6** | 35 | 6 | 58 |
| pallets/click | 7 | **7** | 8 | 6 | 6 |
| encode/starlette | 1 | **1** | 4 | 1 | 2 |
| Textualize/rich | 13 | **13** | 14 | 10 | 8 |
| encode/httpx | 0 | **0** | 6 | 0 | 59 |
| pallets/flask | 7 | **7** | 12 | 6 | 260 |
| pydantic/pydantic | 11 | **11** | 93 | 10 | 112 |
| fastapi/fastapi | 6 | **6** | 30 | 4 | 102 |
| tqdm/tqdm | 1 | 0 | 18 | **1** | 37 |
| **Total** | **52** | **51** | **220** | **44** | **644** |

<br>

| Metric | Skylos | Vulture |
|:---|---:|---:|
| **Recall** | **98.1%** (51/52) | 84.6% (44/52) |
| **False Positives** | **220** | 644 |
| **Dead items found** | **51** | 44 |
| **Precision** | **18.8%** | 6.4% |

**Skylos finds 7 more dead items with 3x fewer false positives.**

### Where the gap is largest

| Repo | Vulture FP | Skylos FP | What Vulture flags incorrectly |
|:---|---:|---:|:---|
| **flask** | 260 | **12** | Jinja2 template globals, Werkzeug protocol methods |
| **pydantic** | 112 | **93** | Config annotations, `TYPE_CHECKING` imports, mypy hooks |
| **fastapi** | 102 | **30** | 100+ OpenAPI model fields (`maxLength`, `exclusiveMinimum`) |
| **httpx** | 59 | **6** | Transport/auth protocol methods |
| **requests** | 58 | **35** | `__init__.py` re-exports, Sphinx `conf.py` variables |

### Where Skylos still loses (honestly)

| Repo | Skylos FP | Vulture FP | Why |
|:---|---:|---:|:---|
| **click** | 8 | **6** | IO protocol methods on `io.RawIOBase` subclasses |
| **starlette** | 4 | **2** | Instance method calls not resolved to class definitions |
| **rich** | 14 | **8** | Sentinel vars checked via `f_locals.get("name")` |
| **tqdm** | 18 | 37 | Skylos misses 1 dead function (suppressed as re-export) |

---

## Results: TypeScript (Skylos vs Knip)

> Benchmarked on [unjs/consola](https://github.com/unjs/consola) — 7,200 stars, 21 files, ~2,050 LOC.

Ground truth: 4 dead items (entire orphaned `src/utils/format.ts` module), 31 confirmed-alive items.

| Metric | Skylos | Knip |
|:---|---:|---:|
| **True Positives** | **4** | **4** |
| **False Positives** | **7** | 8 |
| **False Negatives** | **0** | **0** |
| **Precision** | **36.4%** | 7.5% |
| **Recall** | **100%** | **100%** |
| **F1 Score** | **53.3%** | 14.0% |
| **Speed** | **6.83s** | 11.08s |

Both tools achieve 100% recall. Skylos has **~5x better precision**.

**Why Knip struggles here:** Its `package.json` exports point to `dist/` not `src/`, so Knip can't trace entry points — it flags `basic.ts`, `browser.ts`, `core.ts` as dead files and reports public API re-exports as unused.

**Why Skylos has FPs:** Same-file variable references it can't resolve (e.g. `TYPE_COLOR_MAP` used via `(TYPE_COLOR_MAP as any)[logObj.type]` on the same page).

---

## Synthetic Benchmark: Polyglot Monorepo

A controlled environment with planted dead code to test harder patterns.

**Setup:** Python (FastAPI) + TypeScript (Express) monorepo with:
- 150 ground-truth dead-code items (110 Python + 40 TypeScript)
- 22 dynamic dispatch traps (getattr, globals, `__init_subclass__`, decorators, bracket notation)
- Optional LLM verification layer

### Results

| Configuration | Precision | Recall | F1 | Speed | FPs | Dynamic Dispatch |
|:---|---:|---:|---:|---:|---:|---:|
| **Skylos Hybrid High-Conf** | **67.4%** | **93.9%** | **78.5%** | 419s | **2** | **8/8** |
| Skylos Static (conf=10) | 52.5% | 93.9% | 67.4% | 2s | 13 | 0/8 |
| Skylos Static (conf=60) | 72.7% | 72.7% | 72.7% | 2s | 9 | 0/8 |
| Vulture | 38.5% | 75.8% | 50.8% | 0.1s | 14 | 0/8 |

**Key takeaway:** LLM verification eliminates **84.6% of false positives** (13 -> 2) with zero recall cost. It catches all 8 dynamic dispatch patterns that fool static analysis.

### What are the dynamic dispatch traps?

Static analysis sees 0 references and flags as dead. But these are called at runtime:

```python
# getattr() dispatch — static sees 0 refs to export_csv
def export_csv(data): ...
def run_export(fmt):
    handler = getattr(sys.modules[__name__], f"export_{fmt}")
    return handler(data)

# globals() dict — static sees 0 refs to handle_create
HANDLER_MAP = { action: globals()[f"handle_{action}"]
                for action in ("create", "update", "delete") }

# __init_subclass__ — static sees 0 refs to EmailHandler
class Base:
    def __init_subclass__(cls): REGISTRY[cls.name] = cls
class EmailHandler(Base): name = "email"
```

The LLM reads the source file, recognizes the dynamic pattern, and correctly marks them as alive.

---

## Reproduce Any Benchmark

```bash
# Real-world repos (Python)
cd real_life_examples/{repo} && python3 ../benchmark_{repo}.py

# Real-world (TypeScript)
cd real_life_examples/consola && python3 ../benchmark_consola.py

# Synthetic monorepo
python benchmark_hybrid.py --confidence 10

# Requirements
pip install skylos vulture    # Python benchmarks
npm install -g knip           # TypeScript benchmarks
```

---

## Methodology

1. **Define ground truth** — `EXPECTED_UNUSED` (truly dead symbols) and `ACTUALLY_USED` (confirmed alive) curated per repo
2. **Run tools** — Skylos, Vulture/Knip with JSON output
3. **Normalize** — Consistent paths, canonicalized alias names
4. **Score** — TP/FP/FN, precision, recall, F1

### What counts as a false positive?

Patterns that cause other tools to report noise:

| Pattern | Example | Affected Repos |
|:---|:---|:---|
| Re-export barrels | `__init__.py` re-exports | requests, rich |
| Framework callbacks | Keras/Dask/ASGI | tqdm, fastapi, starlette |
| Model field annotations | Pydantic `BaseModel` attrs | pydantic, fastapi |
| Dynamic attribute access | `__getattr__`, `getattr()`, `f_locals` | pydantic, rich |
| Protocol methods | `io.RawIOBase`, transport interfaces | click, httpx |
| Template globals | Jinja2 template vars | flask |
| `as any` casts | `(MAP as any)[key]` | consola |
| package.json -> dist/ | Entry points not in src/ | consola |

---

<details>
<summary><strong>Full list of planted dead code (synthetic monorepo)</strong></summary>

### Unused Imports

**Python (8):** `math` (logging.py), `datetime` (notes.py), `get_settings` (deps.py), `Session` (deps.py), `fmt_money` (reports.py), `flask` (bootstrap.py), `sys` (bootstrap.py), `Tuple` (slack.py)

**TypeScript (6):** `path` (logging.ts), `URL` (notes.ts), `loadConfig` (auth.ts), `formatMoney` (reports.ts), `express` (bootstrap.ts), `EventEmitter` (slack.ts)

### Unused Functions

**Python (63):** `_is_prod`, `_parse_cors_origins`, `get_actor_from_headers`, `_normalize_query`, `generate_report`, `_drop_all`, `get_engine_info`, `_reset_sequences`, `_row_to_dict`, `bulk_create_notes`, `_build_search_query`, `_validate_title`, `normalize_and_score_query`, `slugify`, `new_request_id`, `weak_token`, `format_money`, `process`, `run_payment`, `not_found`, `request_text`, `verify_hmac_sha256_prefixed`, `build_finding_blocks`, `find_issue_by_title`, `timed_request`, `snapshot_metrics`, `add_tags`, `_build_header`, `_build_footer`, `generate_report_v1`, `_search_v2`, `generate_correlation_id`, `validate_input`, `deprecate`, `generate_daily_report`, `sync_external_contacts`, `cleanup_expired_sessions`, `invalidate_cache_for`, `get_all_flags`, `_evaluate_flag_with_context`, `on_note_deleted_cleanup`, `on_user_signed_up_welcome`, `apply_filters`, `validate_bearer_token`, `generate_api_token`, `check_ip_allowlist`, `list_plugins`, `unload_plugin`, `send_bulk_notifications`, `schedule_notification`, `_render_template`, `query_audit_log`, `_redact_sensitive_fields`, `export_audit_csv`, `mock_redis`, `admin_user`, `random_email`, `assert_paginated_response`, `wait_for_event`, `mock_external_service`, `test_create_note_with_tags`, `test_bulk_import_notes`, `_seed_notes`

**TypeScript (24):** `_isProd`, `getActorFromHeaders`, `_normalizeQuery`, `_dropAll`, `_rowToObject`, `_validateTitle`, `slugify`, `formatMoney`, `process`, `runPayment`, `notFound`, `requestText`, `getHttpClient`, `verifyHmacSha256Prefixed`, `buildFindingBlocks`, `authHeaders`, `findIssueByTitle`, `snapshotMetrics`, `timedRequest`, `_buildHeader`, `_buildFooter`, `generateReportV1`, `_searchV2`

### Unused Variables

**Python (17):** `APP_DISPLAY_NAME`, `MAX_UPLOAD_SIZE`, `DEFAULT_PAGE_SIZE`, `DB_POOL_SIZE`, `DEFAULT_REQUEST_ID`, `DEFAULT_HEADERS`, `_queue_depth`, `TASK_PRIORITY_HIGH`, `TASK_PRIORITY_LOW`, `FLAG_ADMIN_ENDPOINT`, `EVENT_NOTE_ARCHIVED`, `ROLE_VIEWER`, `TOKEN_ALGORITHM`, `MAX_BATCH_SIZE`, `AUDIT_RETENTION_DAYS`, `TEST_TIMEOUT`, `SLOW_TEST_THRESHOLD`

**TypeScript (5):** `APP_DISPLAY_NAME`, `DEFAULT_PAGE_SIZE`, `DEFAULT_REQUEST_ID`, `DEFAULT_HEADERS`, `_queueDepth`

### Unused Classes

**Python (22):** `DemoError`, `Tag`, `Comment`, `Attachment`, `NoteInternal`, `NotePatch`, `NoteSearch`, `PayPal`, `CorrelationIdMiddleware`, `RateLimitMiddleware`, `MongoNoteRepository`, `PagerDutyNotifier`, `RedisCache`, `AuthenticationError`, `AuthorizationError`, `RateLimitError`, `ExternalServiceError`, `CursorParams`, `CursorResult`, `NotificationLog`, `UserFactory`, `TagFactory`

**TypeScript (6):** `DemoError`, `Tag`, `NoteInternal`, `AppConfig`, `RequestContext`, `PaginationParams`

### Intentional Security Findings (for demo)

- SQL injection via f-string in `search_notes`
- SSRF via untrusted URL fetch in `fetch_url`
- Path traversal in `read_file`
- Weak randomness in `weak_token`

</details>

<details>
<summary><strong>Known limitations</strong></summary>

**Transitive dead code (2 false negatives):**
`_build_header` and `_build_footer` are only called by dead `generate_report_v1`. Requires graph-based propagation (work in progress).

**Imported but unused (2 remaining FPs):**
`search` and `new_request_id` are imported in main.py but never called. The LLM cannot detect these without cross-file import analysis.

</details>

---

## Citation

```
Skylos Dead-Code Detection Benchmark
https://github.com/duriantaco/skylos-demo
Ground-truthed evaluation of static dead code detection
```
