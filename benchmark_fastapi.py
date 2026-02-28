#!/usr/bin/env python3

import json
import os
import re
import subprocess
import time
from pathlib import Path

SKYLOS_CONFIDENCE = 20

EXPECTED_UNUSED = {
    "functions": [],
    "variables": [
        ("fastapi/exceptions.py", "RequestErrorModel"),
        ("fastapi/exceptions.py", "WebSocketErrorModel"),
        ("fastapi/openapi/utils.py", "cb_security_schemes"),
        ("fastapi/openapi/utils.py", "cb_definitions"),
    ],
    "imports": [
        ("fastapi/_compat/v2.py", "PydanticUndefinedAnnotation"),
        ("fastapi/_compat/v2.py", "GetJsonSchemaHandler"),
    ],
    "classes": [],
}


ACTUALLY_USED = [
    ("fastapi/_compat/v2.py", "Url"),
    ("fastapi/_compat/v2.py", "with_info_plain_validator_function"),
    ("fastapi/_compat/v2.py", "bytes_schema"),
    ("fastapi/_compat/v2.py", "model_name_map"),
    ("fastapi/applications.py", "req"),
    ("fastapi/applications.py", "middleware_type"),
    ("fastapi/exception_handlers.py", "request"),
    ("fastapi/routing.py", "receive"),
    ("fastapi/routing.py", "send"),
    ("fastapi/routing.py", "exc_info"),
    ("fastapi/datastructures.py", "file"),
    ("fastapi/datastructures.py", "filename"),
    ("fastapi/datastructures.py", "size"),
    ("fastapi/datastructures.py", "content_type"),
    ("fastapi/datastructures.py", "source"),
    ("fastapi/datastructures.py", "_"),
    ("fastapi/openapi/models.py", "EmailStr"),
    ("fastapi/openapi/models.py", "_"),
    ("fastapi/openapi/models.py", "SchemaOrBool"),
    ("fastapi/openapi/models.py", "bearerFormat"),
    ("fastapi/openapi/models.py", "openIdConnectUrl"),
    ("fastapi/openapi/models.py", "propertyName"),
    ("fastapi/openapi/models.py", "mapping"),
    ("fastapi/openapi/models.py", "namespace"),
    ("fastapi/openapi/models.py", "attribute"),
    ("fastapi/openapi/models.py", "wrapped"),
    ("fastapi/openapi/models.py", "url"),
    ("fastapi/openapi/models.py", "schema_"),
    ("fastapi/openapi/models.py", "vocabulary"),
    ("fastapi/openapi/models.py", "anchor"),
    ("fastapi/openapi/models.py", "dynamicAnchor"),
    ("fastapi/openapi/models.py", "dynamicRef"),
    ("fastapi/openapi/models.py", "ref"),
    ("fastapi/openapi/models.py", "defs"),
    ("fastapi/openapi/models.py", "comment"),
    ("fastapi/openapi/models.py", "allOf"),
    ("fastapi/openapi/models.py", "anyOf"),
    ("fastapi/openapi/models.py", "oneOf"),
    ("fastapi/openapi/models.py", "not_"),
    ("fastapi/openapi/models.py", "if_"),
    ("fastapi/openapi/models.py", "then"),
    ("fastapi/openapi/models.py", "else_"),
    ("fastapi/openapi/models.py", "dependentSchemas"),
    ("fastapi/openapi/models.py", "prefixItems"),
    ("fastapi/openapi/models.py", "contains"),
    ("fastapi/openapi/models.py", "properties"),
    ("fastapi/openapi/models.py", "patternProperties"),
    ("fastapi/openapi/models.py", "additionalProperties"),
    ("fastapi/openapi/models.py", "propertyNames"),
    ("fastapi/openapi/models.py", "unevaluatedItems"),
    ("fastapi/openapi/models.py", "unevaluatedProperties"),
    ("fastapi/openapi/models.py", "const"),
    ("fastapi/openapi/models.py", "multipleOf"),
    ("fastapi/openapi/models.py", "maximum"),
    ("fastapi/openapi/models.py", "exclusiveMaximum"),
    ("fastapi/openapi/models.py", "minimum"),
    ("fastapi/openapi/models.py", "exclusiveMinimum"),
    ("fastapi/openapi/models.py", "maxLength"),
    ("fastapi/openapi/models.py", "minLength"),
    ("fastapi/openapi/models.py", "maxItems"),
    ("fastapi/openapi/models.py", "minItems"),
    ("fastapi/openapi/models.py", "uniqueItems"),
    ("fastapi/openapi/models.py", "maxContains"),
    ("fastapi/openapi/models.py", "minContains"),
    ("fastapi/openapi/models.py", "maxProperties"),
    ("fastapi/openapi/models.py", "minProperties"),
    ("fastapi/openapi/models.py", "dependentRequired"),
    ("fastapi/openapi/models.py", "contentEncoding"),
    ("fastapi/openapi/models.py", "contentMediaType"),
    ("fastapi/openapi/models.py", "contentSchema"),
    ("fastapi/openapi/models.py", "readOnly"),
    ("fastapi/openapi/models.py", "writeOnly"),
    ("fastapi/openapi/models.py", "xml"),
    ("fastapi/openapi/models.py", "externalDocs"),
    ("fastapi/openapi/models.py", "externalValue"),
    ("fastapi/openapi/models.py", "contentType"),
    ("fastapi/openapi/models.py", "style"),
    ("fastapi/openapi/models.py", "explode"),
    ("fastapi/openapi/models.py", "allowReserved"),
    ("fastapi/openapi/models.py", "encoding"),
    ("fastapi/openapi/models.py", "operationRef"),
    ("fastapi/openapi/models.py", "operationId"),
    ("fastapi/openapi/models.py", "requestBody"),
    ("fastapi/openapi/models.py", "server"),
    ("fastapi/openapi/models.py", "links"),
    ("fastapi/openapi/models.py", "security"),
    ("fastapi/openapi/models.py", "implicit"),
    ("fastapi/openapi/models.py", "clientCredentials"),
    ("fastapi/openapi/models.py", "authorizationCode"),
    ("fastapi/openapi/models.py", "schemas"),
    ("fastapi/openapi/models.py", "requestBodies"),
    ("fastapi/openapi/models.py", "securitySchemes"),
    ("fastapi/openapi/models.py", "pathItems"),
    ("fastapi/openapi/models.py", "jsonSchemaDialect"),
    ("fastapi/openapi/models.py", "source"),
    ("fastapi/openapi/models.py", "identifier"),
    ("fastapi/openapi/models.py", "termsOfService"),
    ("fastapi/openapi/models.py", "license"),
    ("fastapi/openapi/models.py", "variables"),
    ("fastapi/openapi/utils.py", "generate_operation_id"),
    ("fastapi/middleware/wsgi.py", "WSGIMiddleware"),
    ("fastapi/param_functions.py", "deprecated"),
    ("fastapi/types.py", "IncEx"),
    ("fastapi/responses.py", "UJSONResponse"),
    ("fastapi/responses.py", "render"),
    ("fastapi/responses.py", "ORJSONResponse"),
    ("fastapi/security/base.py", "SecurityBase"),
    ("fastapi/applications.py", "middleware_stack"),
    ("fastapi/applications.py", "build_middleware_stack"),
    ("fastapi/applications.py", "websocket_route"),
    ("fastapi/applications.py", "state"),
    ("fastapi/applications.py", "exception_handler"),
    ("fastapi/routing.py", "websocket_route"),
    ("fastapi/routing.py", "param_convertors"),
    ("fastapi/routing.py", "path_regex"),
    ("fastapi/security/oauth2.py", "scope_str"),
    ("fastapi/exceptions.py", "function"),
    ("fastapi/exceptions.py", "file"),
    ("fastapi/exceptions.py", "line"),
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
    r = _run(["skylos", "fastapi/", "--json", f"--min-confidence={SKYLOS_CONFIDENCE}"])
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
    au_set = {(f, n) for f, n in ACTUALLY_USED}
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
    r = _run(["python3", "-m", "vulture", "fastapi/", "--min-confidence=60"])
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
    au_set = {(f, n) for f, n in ACTUALLY_USED}
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
    os.chdir(Path(__file__).resolve().parent / "fastapi")
    total_dead = sum(len(v) for v in EXPECTED_UNUSED.values())
    print(f"\n{'=' * 60}")
    print(f" FastAPI benchmark — {total_dead} confirmed dead items")
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
