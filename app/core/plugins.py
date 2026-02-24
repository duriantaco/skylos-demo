from __future__ import annotations

from typing import Any

_plugin_store: dict[str, Any] = {}


def load_plugin(name: str) -> None:
    _plugin_store[name] = {"name": name, "loaded": True}
    print(f"[plugin] Loaded: {name}")


def list_plugins() -> list[str]:  # UNUSED (demo)
    return list(_plugin_store.keys())


def get_plugin(name: str) -> Any | None:
    return _plugin_store.get(name)


def unload_plugin(name: str) -> bool:  # UNUSED (demo)
    if name in _plugin_store:
        del _plugin_store[name]
        print(f"[plugin] Unloaded: {name}")
        return True
    return False
