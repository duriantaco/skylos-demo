from __future__ import annotations

from typing import Any

_flag_store: dict[str, bool] = {
    "v2_health": False,
    "dark_mode": True,
    "beta_export": False,
}

FLAG_ADMIN_ENDPOINT = "admin_endpoint"  # UNUSED (demo)


def is_enabled(flag_name: str) -> bool:
    return _flag_store.get(flag_name, False)


def _evaluate_flag_with_context(
    flag_name: str, context: dict[str, Any] | None = None
) -> bool:  # UNUSED (demo)
    base = _flag_store.get(flag_name, False)
    if not base or context is None:
        return base
    if context.get("role") == "admin":
        return True
    return base


def get_all_flags() -> dict[str, bool]:  # UNUSED (demo)
    return dict(_flag_store)
