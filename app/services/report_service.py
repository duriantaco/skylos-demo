def _build_header(title: str) -> str:
    ## UNUSED: Only called by generate_report_v1 which is also dead
    return f"=== {title.upper()} ==="


def _build_footer(title: str) -> str:
    ## UNUSED: only called by generate_report_v1 which is also dead
    return f"--- {title} ---"


def generate_report_v1(title: str, body: str) -> str:
    ## UNUSED: never called from anywhere in the project
    header = _build_header(title)
    footer = _build_footer(title)
    return f"{header}\n{body}\n{footer}"


def _search_v2(query: str) -> list:
    ## UNUSED: called inside an `if False:` branch that never executes
    return [f"v2-result-for-{query}"]


def search(query: str) -> list:
    if False:  # was: if ENABLE_V2_SEARCH
        return _search_v2(query)
    return [f"basic-result-for-{query}"]
