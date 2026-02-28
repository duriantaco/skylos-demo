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
        # Deprecated
        ("pydantic/_internal/_typing_extra.py", "eval_type_lenient"),
        # Deprecated
        ("pydantic/v1/utils.py", "truncate"),
    ],
    "variables": [
        ("pydantic/_internal/_core_utils.py", "AnyFunctionSchema"),
        ("pydantic/_internal/_core_utils.py", "pps"),
        ("pydantic/_internal/_typing_extra.py", "origin_is_union"),
        ("pydantic/plugin/_schema_validator.py", "events"),
        ("pydantic/v1/schema.py", "default_prefix"),
        ("pydantic/v1/schema.py", "m_nested_models"),
        ("pydantic/v1/schema.py", "json_scheme"),
    ],
    "imports": [],
    "classes": [
        ("pydantic/_internal/_generics.py", "DeepChainMap"),
        ("pydantic/v1/decorator.py", "CustomConfig"),
    ],
}

ACTUALLY_USED = [
    ("pydantic/_internal/_generics.py", "LimitedDict"),
    ("pydantic/_internal/_generics.py", "recursively_defined_type_refs"),
    ("pydantic/_internal/_config.py", "str_to_lower"),
    ("pydantic/_internal/_config.py", "str_to_upper"),
    ("pydantic/_internal/_config.py", "str_strip_whitespace"),
    ("pydantic/_internal/_config.py", "str_min_length"),
    ("pydantic/_internal/_config.py", "str_max_length"),
    ("pydantic/_internal/_config.py", "loc_by_alias"),
    ("pydantic/_internal/_config.py", "revalidate_instances"),
    ("pydantic/_internal/_config.py", "ser_json_temporal"),
    ("pydantic/_internal/_config.py", "val_temporal_unit"),
    ("pydantic/_internal/_config.py", "val_json_bytes"),
    ("pydantic/_internal/_config.py", "ser_json_inf_nan"),
    ("pydantic/_internal/_config.py", "hide_input_in_errors"),
    ("pydantic/_internal/_config.py", "coerce_numbers_to_str"),
    ("pydantic/_internal/_config.py", "regex_engine"),
    ("pydantic/_internal/_config.py", "validation_error_cause"),
    ("pydantic/_internal/_config.py", "cache_strings"),
    ("pydantic/_internal/_config.py", "serialize_by_alias"),
    ("pydantic/_internal/_config.py", "url_preserve_empty_path"),
    ("pydantic/config.py", "str_to_lower"),
    ("pydantic/config.py", "str_to_upper"),
    ("pydantic/config.py", "str_strip_whitespace"),
    ("pydantic/config.py", "str_min_length"),
    ("pydantic/config.py", "str_max_length"),
    ("pydantic/config.py", "loc_by_alias"),
    ("pydantic/config.py", "revalidate_instances"),
    ("pydantic/config.py", "ser_json_temporal"),
    ("pydantic/config.py", "val_temporal_unit"),
    ("pydantic/config.py", "val_json_bytes"),
    ("pydantic/config.py", "ser_json_inf_nan"),
    ("pydantic/config.py", "hide_input_in_errors"),
    ("pydantic/config.py", "regex_engine"),
    ("pydantic/config.py", "validation_error_cause"),
    ("pydantic/config.py", "cache_strings"),
    ("pydantic/config.py", "serialize_by_alias"),
    ("pydantic/config.py", "url_preserve_empty_path"),
    ("pydantic/config.py", "schema_dialect"),
    ("pydantic/_internal/_discriminated_union.py", "CoreMetadata"),
    ("pydantic/_internal/_model_construction.py", "PydanticExtraInfo"),
    ("pydantic/_internal/_namespace_utils.py", "ParamSpec"),
    ("pydantic/_internal/_namespace_utils.py", "TypeVarTuple"),
    ("pydantic/_internal/_schema_gather.py", "ComputedField"),
    ("pydantic/_internal/_schema_gather.py", "SerSchema"),
    ("pydantic/_internal/_typing_extra.py", "eval_type_backport"),
    ("pydantic/types.py", "CoreMetadata"),
    ("pydantic/functional_serializers.py", "partial"),
    ("pydantic/functional_serializers.py", "partialmethod"),
    ("pydantic/v1/fields.py", "ModelOrDc"),
    ("pydantic/v1/fields.py", "ValidatorsList"),
    ("pydantic/v1/main.py", "Signature"),
    ("pydantic/v1/main.py", "ValidatorListDict"),
    ("pydantic/v1/schema.py", "Dataclass"),
    ("pydantic/v1/typing.py", "_TypingBase"),
    ("pydantic/v1/utils.py", "Dataclass"),
    ("pydantic/v1/utils.py", "ModelField"),
    ("pydantic/v1/mypy.py", "TypeVarDef"),
    ("pydantic/v1/mypy.py", "TypingType"),
    ("pydantic/_internal/_known_annotated_metadata.py", "SEQUENCE_CONSTRAINTS"),
    ("pydantic/_internal/_known_annotated_metadata.py", "TIMEDELTA_CONSTRAINTS"),
    ("pydantic/_internal/_known_annotated_metadata.py", "TIME_CONSTRAINTS"),
    ("pydantic/_internal/_known_annotated_metadata.py", "check_metadata"),
    ("pydantic/_internal/_core_metadata.py", "pydantic_js_prefer_positional_arguments"),
    ("pydantic/_internal/_core_metadata.py", "pydantic_internal_union_tag_key"),
    ("pydantic/_internal/_core_metadata.py", "pydantic_internal_union_discriminator"),
    ("pydantic/_internal/_typing_extra.py", "is_class"),
    ("pydantic/annotated_handlers.py", "maybe_ref_json_schema"),
    ("pydantic/annotated_handlers.py", "maybe_ref_schema"),
    ("pydantic/root_model.py", "include"),
    ("pydantic/root_model.py", "by_alias"),
    ("pydantic/root_model.py", "exclude_unset"),
    ("pydantic/root_model.py", "exclude_defaults"),
    ("pydantic/root_model.py", "exclude_none"),
    ("pydantic/root_model.py", "exclude_computed_fields"),
    ("pydantic/root_model.py", "round_trip"),
    ("pydantic/root_model.py", "serialize_as_any"),
    ("pydantic/types.py", "_core_schema"),
    ("pydantic/mypy.py", "plugin"),
    ("pydantic/mypy.py", "get_base_class_hook"),
    ("pydantic/mypy.py", "get_metaclass_hook"),
    ("pydantic/mypy.py", "get_method_hook"),
    ("pydantic/mypy.py", "report_config_data"),
    ("pydantic/mypy.py", "ctx"),
    ("pydantic/mypy.py", "_pydantic_model_class_maker_callback"),
    ("pydantic/mypy.py", "_pydantic_model_metaclass_marker_callback"),
    ("pydantic/mypy.py", "from_attributes_callback"),
    ("pydantic/mypy.py", "DATACLASS_FULLNAME"),
    ("pydantic/mypy.py", "MYPY_VERSION_TUPLE"),
    ("pydantic/mypy.py", "ERROR_FIELD_DEFAULTS"),
    ("pydantic/mypy.py", "error_from_attributes"),
    ("pydantic/mypy.py", "error_unexpected_behavior"),
    ("pydantic/mypy.py", "visit_any"),
    ("pydantic/mypy.py", "is_class"),
    ("pydantic/mypy.py", "is_decorated"),
    ("pydantic/mypy.py", "variance"),
    ("pydantic/mypy.py", "_reason"),
    ("pydantic/mypy.py", "is_property"),
    ("pydantic/v1/mypy.py", "plugin"),
    ("pydantic/v1/mypy.py", "get_base_class_hook"),
    ("pydantic/v1/mypy.py", "get_metaclass_hook"),
    ("pydantic/v1/mypy.py", "get_function_hook"),
    ("pydantic/v1/mypy.py", "get_method_hook"),
    ("pydantic/v1/mypy.py", "get_class_decorator_hook"),
    ("pydantic/v1/mypy.py", "report_config_data"),
    ("pydantic/v1/mypy.py", "ctx"),
    ("pydantic/v1/mypy.py", "_pydantic_model_class_maker_callback"),
    ("pydantic/v1/mypy.py", "_pydantic_model_metaclass_marker_callback"),
    ("pydantic/v1/mypy.py", "_pydantic_field_callback"),
    ("pydantic/v1/mypy.py", "from_orm_callback"),
    ("pydantic/v1/mypy.py", "error_from_orm"),
    ("pydantic/v1/mypy.py", "error_default_and_default_factory_specified"),
    ("pydantic/v1/mypy.py", "is_class"),
    ("pydantic/v1/mypy.py", "is_property"),
    ("pydantic/v1/mypy.py", "is_decorated"),
    ("pydantic/v1/_hypothesis_plugin.py", "resolve_conbytes"),
    ("pydantic/v1/_hypothesis_plugin.py", "resolve_condecimal"),
    ("pydantic/v1/_hypothesis_plugin.py", "resolve_confloat"),
    ("pydantic/v1/_hypothesis_plugin.py", "resolve_conint"),
    ("pydantic/v1/_hypothesis_plugin.py", "resolve_condate"),
    ("pydantic/v1/_hypothesis_plugin.py", "resolve_constr"),
    ("pydantic/experimental/pipeline.py", "datetime_tz"),
    ("pydantic/experimental/pipeline.py", "datetime_with_tz"),
    ("pydantic/experimental/pipeline.py", "str_upper"),
    ("pydantic/experimental/pipeline.py", "str_title"),
    ("pydantic/experimental/pipeline.py", "not_eq"),
    ("pydantic/experimental/pipeline.py", "in_"),
    ("pydantic/experimental/pipeline.py", "not_in"),
    ("pydantic/experimental/pipeline.py", "datetime_tz_naive"),
    ("pydantic/experimental/pipeline.py", "datetime_tz_aware"),
    ("pydantic/experimental/pipeline.py", "str_lower"),
    ("pydantic/experimental/pipeline.py", "str_strip"),
    ("pydantic/experimental/pipeline.py", "str_pattern"),
    ("pydantic/experimental/pipeline.py", "str_contains"),
    ("pydantic/experimental/pipeline.py", "str_starts_with"),
    ("pydantic/experimental/pipeline.py", "str_ends_with"),
    ("pydantic/experimental/arguments_schema.py", "generate_arguments_schema"),
    ("pydantic/json_schema.py", "ValidationsMapping"),
    ("pydantic/json_schema.py", "function_before_schema"),
    ("pydantic/json_schema.py", "function_after_schema"),
    ("pydantic/json_schema.py", "function_plain_schema"),
    ("pydantic/json_schema.py", "function_wrap_schema"),
    ("pydantic/json_schema.py", "default_schema"),
    ("pydantic/json_schema.py", "typed_dict_field_schema"),
    ("pydantic/json_schema.py", "dataclass_field_schema"),
    ("pydantic/json_schema.py", "model_field_schema"),
    ("pydantic/json_schema.py", "computed_field_schema"),
    ("pydantic/json_schema.py", "definition_ref_schema"),
    ("pydantic/json_schema.py", "invalid_schema"),
    ("pydantic/json_schema.py", "tuple_positional_schema"),
    ("pydantic/json_schema.py", "tuple_variable_schema"),
    ("pydantic/json_schema.py", "models_json_schema"),
    ("pydantic/json_schema.py", "Examples"),
    ("pydantic/json_schema.py", "SkipJsonSchema"),
    ("pydantic/main.py", "model_computed_fields"),
    ("pydantic/main.py", "model_fields_set"),
    ("pydantic/main.py", "model_validate_json"),
    ("pydantic/main.py", "model_validate_strings"),
    ("pydantic/main.py", "parse_raw"),
    ("pydantic/main.py", "parse_file"),
    ("pydantic/main.py", "construct"),
    ("pydantic/main.py", "update_forward_refs"),
    ("pydantic/type_adapter.py", "TypeAdapterT"),
    ("pydantic/type_adapter.py", "dump_json"),
    ("pydantic/type_adapter.py", "json_schemas"),
    ("pydantic/color.py", "as_rgb"),
    ("pydantic/color.py", "as_hsl"),
    ("pydantic/networks.py", "encoded_string"),
    ("pydantic/types.py", "masked"),
    ("pydantic/types.py", "human_readable"),
    ("pydantic/types.py", "to"),
    ("pydantic/fields.py", "merge_field_infos"),
    ("pydantic/__init__.py", "__getattr__"),
    ("pydantic/_internal/_decorators.py", "__getattr__"),
    ("pydantic/_internal/_dataclasses.py", "__signature__"),
    ("pydantic/_internal/_model_construction.py", "__signature__"),
    ("pydantic/dataclasses.py", "__getstate__"),
    ("pydantic/_internal/_docs_extraction.py", "visit_AnnAssign"),
    ("pydantic/_internal/_decorators_v1.py", "__values"),
    ("pydantic/_internal/_decorators_v1.py", "__info"),
    ("pydantic/_internal/_decorators_v1.py", "__fields_tuple"),
    ("pydantic/deprecated/class_validators.py", "__cls"),
    ("pydantic/deprecated/class_validators.py", "__values"),
    ("pydantic/deprecated/class_validators.py", "V1RootValidator"),
    ("pydantic/plugin/__init__.py", "input"),
    ("pydantic/plugin/__init__.py", "self_instance"),
    ("pydantic/functional_validators.py", "outer_location"),
    ("pydantic/deprecated/decorator.py", "ConfigType"),
    ("pydantic/deprecated/decorator.py", "check_args"),
    ("pydantic/deprecated/decorator.py", "check_kwargs"),
    ("pydantic/deprecated/decorator.py", "check_positional_only"),
    ("pydantic/deprecated/decorator.py", "check_duplicate_kwargs"),
    ("pydantic/functional_serializers.py", "ModelPlainSerializerWithInfo"),
    ("pydantic/functional_serializers.py", "ModelPlainSerializerWithoutInfo"),
    ("pydantic/functional_serializers.py", "ModelWrapSerializerWithInfo"),
    ("pydantic/functional_serializers.py", "ModelWrapSerializerWithoutInfo"),
    ("pydantic/v1/main.py", "__signature__"),
    ("pydantic/v1/main.py", "parse_raw"),
    ("pydantic/v1/main.py", "parse_file"),
    ("pydantic/v1/main.py", "construct"),
    ("pydantic/v1/main.py", "update_forward_refs"),
    ("pydantic/v1/color.py", "as_rgb"),
    ("pydantic/v1/color.py", "as_hsl"),
    ("pydantic/v1/types.py", "display"),
    ("pydantic/v1/types.py", "masked"),
    ("pydantic/v1/types.py", "human_readable"),
    ("pydantic/v1/types.py", "to"),
    ("pydantic/v1/networks.py", "HostParts"),
    ("pydantic/v1/networks.py", "parts"),
    ("pydantic/v1/networks.py", "validate_port"),
    ("pydantic/v1/networks.py", "ipv4"),
    ("pydantic/v1/networks.py", "ipv6"),
    ("pydantic/v1/networks.py", "domain"),
    ("pydantic/v1/class_validators.py", "ValidatorsList"),
    ("pydantic/v1/class_validators.py", "ValidatorListDict"),
    ("pydantic/v1/config.py", "ConfigType"),
    ("pydantic/v1/config.py", "SchemaExtraCallable"),
    ("pydantic/v1/dataclasses.py", "DataclassT"),
    ("pydantic/v1/dataclasses.py", "DataclassClassOrWrapper"),
    ("pydantic/v1/decorator.py", "ConfigType"),
    ("pydantic/v1/error_wrappers.py", "ErrorDict"),
    ("pydantic/v1/fields.py", "ValidateReturn"),
    ("pydantic/v1/fields.py", "LocStr"),
    ("pydantic/v1/fields.py", "BoolUndefined"),
    ("pydantic/v1/validators.py", "AnyOrderedDict"),
    ("pydantic/v1/validators.py", "Number"),
    ("pydantic/v1/decorator.py", "check_args"),
    ("pydantic/v1/decorator.py", "check_kwargs"),
    ("pydantic/v1/decorator.py", "check_positional_only"),
    ("pydantic/v1/decorator.py", "check_duplicate_kwargs"),
]


def _flat_expected():
    out = set()
    for items in EXPECTED_UNUSED.values():
        for fpath, name in items:
            out.add((fpath, name))
    return out


def _name_only(expected):
    return {name for _, name in expected}


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def run_skylos():
    t0 = time.time()
    r = _run(["skylos", ".", "--json", f"--min-confidence={SKYLOS_CONFIDENCE}"])
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
    expected_names = _name_only(expected)
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
        elif pair in au_set or any(n == name for _, n in au_set):
            fp.append(pair)
        else:
            fp.append(pair)

    return tp, fp, sorted(fn_set)


PAT = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+): unused \w+ '(?P<name>[^']+)' \((?P<conf>\d+)% confidence\)$"
)


def run_vulture():
    t0 = time.time()
    r = _run(["python3", "-m", "vulture", ".", "--min-confidence=60"])
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
    expected_names = _name_only(expected)
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
        elif pair in au_set or any(n == name for _, n in au_set):
            fp.append(pair)
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
    os.chdir(Path(__file__).resolve().parent / "pydantic")
    total_dead = sum(len(v) for v in EXPECTED_UNUSED.values())
    print(f"\n{'=' * 60}")
    print(f" pydantic benchmark — {total_dead} confirmed dead items")
    print(f"{'=' * 60}\n")

    print("Running Skylos …")
    s_items, s_time = run_skylos()

    def _is_src(path):
        p = "/" + path if not path.startswith("/") else path
        return (
            "/tests/" not in p
            and "/test_" not in p
            and "/typechecking/" not in p
            and "/docs/" not in p
            and "/.github/" not in p
            and "/pydantic-core/" not in p
            and "/release/" not in p
        )

    s_src = [i for i in s_items if _is_src(i["file"])]
    s_tp, s_fp, s_fn = classify_skylos(s_src)
    sm = _calc_metrics(s_tp, s_fp, s_fn)
    print(
        f"  Skylos  ({s_time:.1f}s): {len(s_src)} findings | "
        f"TP={sm['TP']} FP={sm['FP']} FN={sm['FN']} | "
        f"Recall={sm['Recall']}  Precision={sm['Precision']}"
    )
    if s_fn:
        print(f"  Missed: {s_fn}")

    print("Running Vulture …")
    v_items, v_time = run_vulture()
    v_src = [i for i in v_items if _is_src(i["file"])]
    v_tp, v_fp, v_fn = classify_vulture(v_src)
    vm = _calc_metrics(v_tp, v_fp, v_fn)
    print(
        f"  Vulture ({v_time:.1f}s): {len(v_src)} findings | "
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
