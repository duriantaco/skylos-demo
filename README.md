## Benchmark: Skylos Dead-Code Detection (Static + Hybrid LLM Mode)

This benchmark evaluates **Skylos** dead-code detection on a realistic FastAPI-style Python repo with:
- **Ground truth validation**: Known unused vs. actually-used symbols
- **Dynamic dispatch patterns**: getattr(), globals(), __init_subclass__ usage that tricks static analysis
- **Hybrid LLM verification**: Optional LLM layer to filter false positives from static analysis

### Key Results Summary

| Configuration | Precision | Recall | F1 Score | Speed | FP Count | Dynamic Dispatch |
|---------------|-----------|--------|----------|-------|----------|------------------|
| **Skylos Hybrid High-Conf**   **67.4%** | **93.9%** | **78.5%** | 419s | **2** | **8/8** |
| Skylos Static (conf=10) | 52.5% | 93.9% | 67.4% | **2s** | 13 | 0/8 |
| Skylos Static (conf=60) | 72.7% | 72.7% | 72.7% | 2s | 9 | 0/8 |
| Vulture | 38.5% | 75.8% | 50.8% | 0.1s | 14 | 0/8 |

**Best Configuration: Skylos Hybrid High-Confidence (conf=10)**
- **+14.9% precision** vs static-only (52.5% → 67.4%)
- **Same recall** (93.9% - no compromise)
- **+27.7% F1 score** vs static-only
- **8/8 dynamic dispatch patterns caught** (vs 0/8 static-only)
- **84.6% false positive reduction** (13 -> 2)

**Trade-off:** Hybrid mode is ~200x slower (2s -> 419s) but eliminates 84.6% of false positives with no recall cost.

### Comparison Modes

1. **Skylos Static**: Traditional static analysis only
2. **Skylos Hybrid**: Static analysis + LLM verification layer
3. **Skylos High-Confidence**: Hybrid mode, showing only LLM-confirmed findings (static∩llm)
4. **Vulture**: Baseline comparison tool

## What are we measuring?

We're measuring **dead-code detection quality** at different **confidence thresholds** and **verification modes**.

### Confidence Thresholds

- **conf=10** (aggressive): Reports all findings including low-confidence ones (maximizes recall)
- **conf=20** (balanced): Filters out very-low-confidence findings
- **conf=60** (conservative): Only high-confidence findings (minimizes false positives)

### Verification Modes

- **Static-only**: Fast, pure static analysis (no LLM calls)
- **Hybrid**: Static + LLM verification of each finding (~200x slower, but filters FPs)
- **High-Confidence (static∩llm)**: Only findings confirmed by BOTH static and LLM


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

# For hybrid mode, set your API key
export OPENAI_API_KEY=your_key_here
# or any other LLM provider supported by litellm
```

### Command-Line Options

The `benchmark_hybrid.py` script supports different confidence levels:

```bash
python benchmark_hybrid.py --help

# Default (confidence=10, with LLM)
python benchmark_hybrid.py

# Test different confidence levels
python benchmark_hybrid.py --confidence 10   # Aggressive (max recall)
python benchmark_hybrid.py --confidence 20   # Balanced
python benchmark_hybrid.py --confidence 60   # Conservative (high precision)

# Static mode
python benchmark_hybrid.py --no-llm
```

### How the Benchmark Results Were Generated

All results in this README were generated using:

```bash
cd skylos-demo
export OPENAI_API_KEY=your_key_here

# Confidence=10 results
python benchmark_hybrid.py --confidence 10

# Confidence=20 results
python benchmark_hybrid.py --confidence 20

# Confidence=60 results
python benchmark_hybrid.py --confidence 60
```

**Timing:**
- Static-only: ~2 seconds
- Hybrid mode: ~7 minutes (makes ~40 LLM API calls, one per zero-reference finding)

### Reproducing the Results

To replicate the exact numbers shown in the benchmark tables:

1. **Clone the repo and install dependencies:**
   ```bash
   git clone <repo-url>
   cd skylos-demo
   pip install skylos
   ```

2. **Set your LLM API key:**
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```

3. **Run the benchmark at each confidence level:**
   ```bash
   # This produces the "Confidence = 10" table
   python benchmark_hybrid.py --confidence 10

   # This produces the "Confidence = 60" table
   python benchmark_hybrid.py --confidence 60
   ```

4. **Expected output:**
   - Benchmark results table (TP/FP/FN, Precision/Recall)
   - LLM impact analysis (FPs caught by LLM)
   - Detailed per-item comparison
   - Dynamic dispatch detection results (8/8 patterns)

---

## Benchmark Results

### Confidence = 10 (Aggressive Mode - Maximize Recall)

| Metric | Skylos Static | Skylos Hybrid | Skylos High-Conf (static∩llm) | Vulture |
|--------|-------------:|-------------:|------------------------------:|--------:|
| **True Positives** | 31 | 31 | 31 | 25 |
| **False Positives** | 13 | 13 | **2** ✅ | 14 |
| **False Negatives** | 2 | 2 | 2 | 8 |
| **Precision** | 52.5% | 52.5% | **67.4%** ✅ | 38.5% |
| **Recall** | 93.9% | 93.9% | 93.9% | 75.8% |
| **F1 Score** | 67.4% | 67.4% | **78.5%** | 50.8% |
| **Speed** | 2.1s | 419s | *(same run)* | 0.1s |

**Key Insight:** LLM verification eliminates **84.6% of false positives** (13 → 2) with **no recall cost**, achieving 67.4% precision vs 52.5% for static-only.

**Dynamic Dispatch Detection:**
- Static: 0/8 patterns caught (100% false positives)
- Hybrid High-Conf: **8/8 patterns caught**

### Confidence = 20 (Balanced Mode)

| Metric | Skylos Static | Skylos Hybrid | Skylos High-Conf (static∩llm) | Vulture |
|--------|-------------:|-------------:|------------------------------:|--------:|
| **True Positives** | 31 | 31 | 31 | 25 |
| **False Positives** | 13 | 13 | 2 | 14 |
| **False Negatives** | 2 | 2 | 2 | 8 |
| **Precision** | 52.5% | 52.5% | **67.4%** | 38.5% |
| **Recall** | 93.9% | 93.9% | 93.9% | 75.8% |
| **F1 Score** | 67.4% | 67.4% | **78.5%** | 50.8% |

> **Note:** At conf=20, results are identical to conf=10 because all 33 expected unused items have confidence ≥10, and no additional findings fall in the 10-19 range.

### Confidence = 60 (Conservative Mode)

| Metric | Skylos Static | Skylos Hybrid | Skylos High-Conf (static∩llm) | Vulture |
|--------|-------------:|-------------:|------------------------------:|--------:|
| **True Positives** | 24 | 24 | 24 | 24 |
| **False Positives** | 9 | 9 | 2 | 14 |
| **False Negatives** | 9 | 9 | 9 | 9 |
| **Precision** | 72.7% | 72.7% | **92.3%** | 63.2% |
| **Recall** | 72.7% | 72.7% | 72.7% | 72.7% |
| **F1 Score** | 72.7% | 72.7% | **81.4%** | 67.6% |

**Trade-off:** Higher threshold improves baseline precision but sacrifices 21.2% recall (missing 7 low-confidence dead code items).

---

## Analysis: Why Hybrid Mode Improves Precision

### The Dynamic Dispatch Problem

Static analysis struggles with patterns where functions are called/referenced dynamically at runtime:

**Pattern 1: getattr() dispatch**
```python
def export_csv(data): ...  # Static sees 0 references
def export_json(data): ...  # Static sees 0 references

def run_export(fmt):
    handler = getattr(sys.modules[__name__], f"export_{fmt}")
    return handler(data)
```

**Pattern 2: globals() dict access**
```python
def handle_create(payload): ...  # Static sees 0 references

HANDLER_MAP = {
    action: globals()[f"handle_{action}"] # Dynamic 
    for action in ("create", "update", "delete")
}
```

**Pattern 3: __init_subclass__ registration**
```python
class Base:
    def __init_subclass__(cls):
        REGISTRY[cls.name] = cls

class EmailHandler(Base):  # registered at import time
    name = "email"
```

### How LLM Verification Catches These

The LLM agent:
1. Receives the full source file for each 0-reference finding
2. Searches for dynamic dispatch patterns (getattr, globals, __init_subclass__)
3. Marks findings as `FALSE_POSITIVE` if dynamic usage is detected
4. Only `TRUE_POSITIVE` (confirmed dead) findings pass to high-confidence output

**Result:** 8/8 dynamic dispatch patterns correctly identified as `FALSE_POSITIVE` → eliminated from high-confidence results.

---

## When to Use Each Mode

### Static-only Mode (Default)
```bash
skylos . --confidence 10
```

**Use when:**
- You want fast results (1-2 seconds)
- You're doing initial exploration or CI/CD checks
- You can tolerate some false positives

**Trade-offs:**
- ✅ Fast (2s for this repo)
- ✅ High recall (93.9%)
- ❌ Lower precision (52.5%) - more false positives
- ❌ Misses dynamic dispatch (8 false positives from patterns)

### Hybrid Mode with High-Confidence Filter
```bash
skylos . --confidence 10 --llm --api-key YOUR_KEY
```

**Use when:**
- Precision matters more than speed
- You're generating reports for manual review
- Your codebase uses dynamic dispatch patterns
- You want to minimize false positive noise

**Trade-offs:**
- ✅ Better precision (67.4%) - fewer false positives
- ✅ Same recall (93.9%)
- ✅ Catches dynamic dispatch patterns
- ❌ Slower (~200x: 419s for this repo)
- ❌ Requires LLM API key and credits

### Conservative Static Mode
```bash
skylos . --confidence 60
```

**Use when:**
- You only want high-confidence findings
- You're okay with missing some dead code
- You want to minimize manual verification

**Trade-offs:**
- ✅ Higher precision (72.7%)
- ❌ Lower recall (72.7%) - misses 7 low-confidence items
- ❌ Still has false positives from dynamic dispatch

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

This repo is structured like a real service:

- FastAPI app entrypoint + router registration
- Layered architecture: routers -> services -> db/crud/models -> schemas
- Typical "real repo" habits:
  - helper functions that are left around but never called
  - unused imports after refactors
  - unused schemas/models from feature churn
  - integration code (webhooks, slack/github clients) with a mix of used + unused helpers

We are explicitly testing:

### 1) Basic dead-code detection
- Unused imports (7 items)
- Unused private helpers (`_normalize_query`, `_row_to_dict`, etc.)
- Unused constants (`DEFAULT_PAGE_SIZE`, `APP_DISPLAY_NAME`, etc.)
- Unused classes and schemas (`DemoError`, `Tag`, `NoteInternal`)

**Why it matters:** This is the bread-and-butter of dead-code tools.

**Expected behavior:**
- Static analysis should catch most of these (high recall)
- LLM verification should confirm them (no false positives expected)

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

**Pattern 4a: getattr() dispatch** (3 test cases)
```python
def export_csv(data): ...  # 0 static references
def export_json(data): ...  # 0 static references
def export_xml(data): ...   # 0 static references

def run_export(fmt):
    handler = getattr(sys.modules[__name__], f"export_{fmt}")
    return handler(data)  # called dynamically
```

**Pattern 4b: globals() dict access** (3 test cases)
```python
def handle_create(payload): ...  # 0 static references
def handle_update(payload): ...  # 0 static references
def handle_delete(payload): ...  # 0 static references

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

**Why it matters:** Static analysis sees 0 references → flags as dead (false positive). Dynamic dispatch is common in:
- Plugin systems and registries
- Format handlers and exporters
- Framework hooks and event handlers
- Command dispatchers and routers

**Expected behavior:**
- **Static-only: 8/8 false positives** (flags all as dead)
- **Hybrid LLM: 0/8 false positives** (correctly identifies dynamic usage)

This is the **key differentiator** for hybrid mode.

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
- **Current state:** Neither static nor LLM catches this (requires graph-based propagation)
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
We don't just eyeball outputs; we compare against a known list of unused and used items (33 expected unused, 14+ actually used).

### Mixed difficulty
It contains:
- **Easy cases** (unused import, unused constant)
- **Medium cases** (unused helper in a services layer, cross-file references)
- **Hard cases** (framework wiring, alias imports, name collisions)
- **Very hard cases** (dynamic dispatch patterns that fool static analysis)

The **dynamic dispatch patterns** (8 test cases) are the key differentiator that tests whether tools can handle real-world Python patterns.

### Fair comparison
We normalize tool outputs to avoid penalizing one tool for naming conventions (e.g. alias reporting).

### Actionable
The outputs directly map to:
- what the tool should catch (true positives)
- what it missed (false negatives)
- what it incorrectly flagged (false positives)

### Tests advanced features
The dynamic dispatch patterns specifically test **LLM-based verification**, which is a novel approach to reducing false positives while maintaining high recall.

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
**Fix:** run tools on `app/` only.

### D) We will evolve the test as Skylos improves
Once Skylos handles these patterns well, we can add additional realistic scenarios:
- dynamically imported plugins (entrypoints / registries)
- pydantic validators and model config usage
- FastAPI dependencies (`Depends(...)`) used via injection
- conditional imports / typing-only imports

---

## Summary

This benchmark evaluates Skylos dead-code detection by:
- **Running static-only and hybrid LLM modes** at different confidence thresholds
- **Testing dynamic dispatch patterns** (getattr, globals, __init_subclass__) that fool static analysis
- **Measuring TP/FP/FN** against curated ground truth (33 expected unused, 14+ actually used)
- **Comparing against Vulture** baseline tool
- **Reporting precision/recall/F1** plus detailed per-item results

### Key Findings

1. **Hybrid LLM verification works**: Eliminates 84.6% of false positives (13 → 2) with no recall cost
2. **Dynamic dispatch is caught**: 8/8 patterns correctly identified by LLM (0/8 by static-only)
3. **Speed trade-off**: Hybrid is ~200x slower but worth it for high-precision use cases
4. **Remaining gaps**: 2 false negatives from transitive dead code (requires graph-based propagation)

### Recommended Configuration

**For CI/CD and fast iteration:**
- `skylos . --confidence 10` (static-only)
- 93.9% recall, 52.5% precision, 2s runtime

**For high-quality reports:**
- `skylos . --confidence 10 --llm` (hybrid with high-conf filter)
- 93.9% recall, 67.4% precision, 419s runtime


## Expected Skylos Findings (Demo)

This repo intentionally contains unused imports / functions / variables / classes so Skylos has something to detect.

> **Warning:** The security issues below are intentionally unsafe for benchmarking. Do **NOT** deploy this repo.


### Unused Imports
- `app/logging.py`: `import math`
- `app/api/routers/notes.py`: `from datetime import datetime`
- `app/api/deps.py`: `from app.config import get_settings`
- `app/api/routers/reports.py`: `from app.utils.formatters import format_money as fmt_money`
- `app/integrations/bootstrap.py", "flask"`
- `app/integrations/bootstrap.py", "sys"`
- `app/integrations/slack.py", "Tuple"`

### Unused Functions
- `app/config.py`: `_is_prod()`
- `app/api/deps.py`: `get_actor_from_headers()`
- `app/api/routers/notes.py`: `_normalize_query()`
- `app/db/session.py`: `_drop_all()`
- `app/db/crud.py`: `_row_to_dict()`
- `app/services/notes_services.py`: `_validate_title()`
- `app/utils/ids.py`: `slugify()`
- `app/utils/formatters.py`: `format_money()`

# Method-name collision / trap case (intentionally dead)
- `app/services/payment_services.py`: `process`

# Integrations (wired in; these remain unused)
- `app/integrations/http_client.py`: `request_text()`
- `app/integrations/webhook_signing.py`: `verify_hmac_sha256_prefixed()`
- `app/integrations/slack.py`: `build_finding_blocks()`
- `app/integrations/github.py`: `find_issue_by_title()`
- `app/integrations/metrics.py`: `timed_request()`

### Unused Variables / Constants
- `app/main.py`: `APP_DISPLAY_NAME`
- `app/db/crud.py`: `DEFAULT_PAGE_SIZE`
- `app/utils/ids.py`: `DEFAULT_REQUEST_ID`

# Integrations (wired in; these remain unused)
- `app/integrations/http_client.py`: `DEFAULT_HEADERS`
- `app/integrations/metrics.py`: `_queue_depth`

### Unused Classes / Models / Schemas
- `app/core/errors.py`: `class DemoError(Exception)`
- `app/db/models.py`: `class Tag(Base)`
- `app/schemas/notes.py`: `class NoteInternal(BaseModel)`

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

**Transitive Dead Code (2 false negatives):**
- `_build_header` - only called by dead `generate_report_v1`
- `_build_footer` - only called by dead `generate_report_v1`

These require graph-based propagation analysis (work in progress).

**Imported but Unused (2 remaining false positives):**
- `search` - imported in main.py but never called
- `new_request_id` - imported in main.py but never called

The LLM cannot detect these without cross-file import analysis.

---

## Citation

If you use this benchmark in your research or tools, please cite:

```
Skylos Dead-Code Detection Benchmark
https://github.com/duriantaco/skylos-demo
Ground-truthed evaluation of static and LLM-hybrid dead code detection
```

