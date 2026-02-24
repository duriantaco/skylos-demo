## v0.3.0 (2026-02-24)

- Expanded Python dead code from 77 → 110 items across 55 files
- Added `tests/` directory (conftest, factories, helpers, test_notes)
- Added `notification_service.py` and `audit_service.py` with getattr dispatch traps
- Grew existing files: models, schemas, config, crud, session
- Reworked all Phase 1 files so dead code is interleaved with live code
- Fixed TypeScript ground truth: 34 → 40 items (added `snapshotMetrics`, `runPayment`, `notFound`, `getHttpClient`, `AppConfig`, `RequestContext`)
- Total ground truth: 150 items (110 Python + 40 TypeScript), 22 dynamic dispatch traps

## v0.2.0 (2026-02-22)

- Added TypeScript Express API (`web/`) with 33 dead-code items and 8 dynamic dispatch traps
- Monorepo benchmark support: combined Python + TypeScript ground truth
- `benchmark_hybrid.py` updated with TS dynamic dispatch items

## v0.1.1 (2026-02-14)

- Added Hybrid LLM verification: 84.6% false positive reduction, 52.5% → 67.4% precision
- Dynamic dispatch pattern detection (getattr, globals, __init_subclass__)
- Lowered confidence threshold support
