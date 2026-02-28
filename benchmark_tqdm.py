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
        # scheduled for removal in tqdm==5.0.0
        ("tqdm/contrib/__init__.py", "builtin_iterable"),
    ],
    "variables": [],
    "imports": [],
    "classes": [],
}

ACTUALLY_USED = [
    ("tqdm/contrib/logging.py", "emit"),
    ("tqdm/contrib/logging.py", "_is_console_logging_handler"),  # called by logging_redirect_tqdm
    (
        "tqdm/contrib/logging.py",
        "_get_first_found_console_logging_handler",
    ),  # called by logging_redirect_tqdm
    ("tqdm/contrib/logging.py", "logging_redirect_tqdm"),
    ("tqdm/contrib/logging.py", "tqdm_logging_redirect"),
    ("tqdm/contrib/__init__.py", "DummyTqdmFile"),
    ("tqdm/dask.py", "_start_state"),  # called by Dask framework
    ("tqdm/dask.py", "_posttask"),
    ("tqdm/dask.py", "_finish"),
    ("tqdm/keras.py", "on_epoch_end"),
    ("tqdm/keras.py", "on_batch_end"),
    ("tqdm/keras.py", "on_train_begin"),
    ("tqdm/keras.py", "on_epoch_begin"),
    ("tqdm/keras.py", "on_train_end"),
    ("tqdm/keras.py", "_implements_train_batch_hooks"),  # Keras optimization hook
    ("tqdm/keras.py", "_implements_test_batch_hooks"),
    ("tqdm/keras.py", "_implements_predict_batch_hooks"),
    ("tqdm/notebook.py", "ipywidgets"),
    ("tqdm/notebook.py", "HBox"),  # parent class of TqdmHBox
    ("tqdm/notebook.py", "_repr_pretty_"),
    ("tqdm/notebook.py", "width"),  # CSS/ipywidgets layout property
    ("tqdm/notebook.py", "flex"),
    ("tqdm/notebook.py", "flex_flow"),  # CSS/ipywidgets layout property
    ("tqdm/notebook.py", "visible"),
    ("tqdm/notebook.py", "visibility"),
    ("tqdm/rich.py", "render"),  # called by rich.progress.Progress
    ("tqdm/_monitor.py", "daemon"),
    ("tqdm/_monitor.py", "woken"),
    ("tqdm/_monitor.py", "run"),
    ("tqdm/asyncio.py", "gather"),
    ("tqdm/std.py", "create_th_lock"),  # deprecated but public API
    ("tqdm/std.py", "progress_apply"),  # monkey-patched onto pandas
    ("tqdm/std.py", "progress_map"),
    ("tqdm/std.py", "progress_applymap"),
    ("tqdm/std.py", "progress_aggregate"),
    ("tqdm/std.py", "progress_transform"),
    ("tqdm/std.py", "unpause"),
    ("tqdm/std.py", "set_description"),
    ("tqdm/std.py", "set_postfix_str"),  # public API, tested
    ("tqdm/std.py", "wrapattr"),
    ("tqdm/tk.py", "set_description"),
    ("tqdm/utils.py", "_environ_cols_wrapper"),  # re-exported in _utils.py
    ("tqdm/cli.py", "importlib_resources"),  # aliased to resources, used
]


def _flat_expected():
    out = set()
    for items in EXPECTED_UNUSED.values():
        for fpath, name in items:
            out.add((fpath, name))
    return out


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def run_skylos():
    t0 = time.time()
    r = _run(["skylos", "tqdm/", "--json", f"--min-confidence={SKYLOS_CONFIDENCE}"])
    elapsed = time.time() - t0
    data = json.loads(r.stdout)
    items = []
    for cat in (
        "unused_functions",
        "unused_imports",
        "unused_classes",
        "unused_variables",
        "unused_parameters",
    ):
        for it in data.get(cat, []):
            it["_cat"] = cat
            items.append(it)
    return items, elapsed


def classify_skylos(items):
    expected = _flat_expected()
    tp, fp, fn_set = [], [], set(expected)

    for it in items:
        raw = it["file"]
        name = it["name"].split(".")[-1]
        rel = os.path.relpath(raw)
        pair = (rel, name)
        if pair in expected:
            tp.append(pair)
            fn_set.discard(pair)
        else:
            fp.append(pair)
    return tp, fp, sorted(fn_set)


PAT = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+): unused \w+ '(?P<name>[^']+)' \((?P<conf>\d+)% confidence\)$"
)


def run_vulture():
    t0 = time.time()
    r = _run(["python3", "-m", "vulture", "tqdm/", "--min-confidence=60"])
    elapsed = time.time() - t0
    items = []
    seen = set()
    for ln in r.stdout.splitlines():
        m = PAT.match(ln)
        if not m:
            continue
        f, name = m.group("file"), m.group("name")
        key = (f, name)
        if key not in seen:
            seen.add(key)
            items.append({"file": f, "name": name, "conf": int(m.group("conf"))})
    return items, elapsed


def classify_vulture(items):
    expected = _flat_expected()
    tp, fp, fn_set = [], [], set(expected)

    for it in items:
        raw = it["file"]
        name = it["name"]
        rel = os.path.relpath(raw)
        pair = (rel, name)
        if pair in expected:
            tp.append(pair)
            fn_set.discard(pair)
        else:
            fp.append(pair)
    return tp, fp, sorted(fn_set)


def _calc_metrics(tp, fp, fn):
    total_dead = len(tp) + len(fn)
    recall = len(tp) / total_dead * 100 if total_dead else 0
    prec = len(tp) / (len(tp) + len(fp)) * 100 if (len(tp) + len(fp)) else 0
    return {
        "TP": len(tp),
        "FP": len(fp),
        "FN": len(fn),
        "Recall": f"{recall:.1f}%",
        "Precision": f"{prec:.1f}%",
    }


def main():
    os.chdir(Path(__file__).resolve().parent / "tqdm")
    total_dead = sum(len(v) for v in EXPECTED_UNUSED.values())
    print(f"\n{'=' * 60}")
    print(f" tqdm benchmark — {total_dead} confirmed dead items")
    print(f"{'=' * 60}\n")

    print("Running Skylos …")
    s_items, s_time = run_skylos()
    s_tp, s_fp, s_fn = classify_skylos(s_items)
    sm = _calc_metrics(s_tp, s_fp, s_fn)
    print(
        f"  Skylos  ({s_time:.1f}s): {len(s_items)} findings | "
        f"TP={sm['TP']} FP={sm['FP']} FN={sm['FN']} | "
        f"Recall={sm['Recall']}  Precision={sm['Precision']}"
    )
    if s_fn:
        print(f"  Missed: {s_fn}")

    print("Running Vulture …")
    v_items, v_time = run_vulture()
    v_tp, v_fp, v_fn = classify_vulture(v_items)
    vm = _calc_metrics(v_tp, v_fp, v_fn)
    print(
        f"  Vulture ({v_time:.1f}s): {len(v_items)} findings | "
        f"TP={vm['TP']} FP={vm['FP']} FN={vm['FN']} | "
        f"Recall={vm['Recall']}  Precision={vm['Precision']}"
    )
    if v_fn:
        print(f"  Missed: {v_fn}")

    print(f"\n{'─' * 60}")
    print(f"  Ground truth dead items: {total_dead}")
    print(
        f"  Skylos : TP={sm['TP']:>3}  FP={sm['FP']:>3}  Recall={sm['Recall']}  Precision={sm['Precision']}"
    )
    print(
        f"  Vulture: TP={vm['TP']:>3}  FP={vm['FP']:>3}  Recall={vm['Recall']}  Precision={vm['Precision']}"
    )
    print(f"{'─' * 60}\n")

    au_set = {(f, n) for f, n in ACTUALLY_USED}
    s_other = [(f, n) for f, n in s_fp if (f, n) not in au_set]
    v_other = [(f, n) for f, n in v_fp if (f, n) not in au_set]
    if s_other:
        print("Skylos other findings (not in ground truth):")
        for f, n in sorted(s_other):
            print(f"  {f}: {n}")
    if v_other:
        print("Vulture other findings (not in ground truth):")
        for f, n in sorted(v_other):
            print(f"  {f}: {n}")

    return sm, vm


if __name__ == "__main__":
    main()
