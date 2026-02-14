def export_csv(data: list) -> str:
    return "\n".join(",".join(str(v) for v in row) for row in data)


def export_json(data: list) -> str:
    import json

    return json.dumps(data)


def export_xml(data: list) -> str:
    return "<data>" + "".join(f"<item>{r}</item>" for r in data) + "</data>"


def run_export(data: list, fmt: str) -> str:
    import sys

    handler = getattr(sys.modules[__name__], f"export_{fmt}", None)
    if handler is None:
        raise ValueError(f"Unknown export format: {fmt}")
    return handler(data)
