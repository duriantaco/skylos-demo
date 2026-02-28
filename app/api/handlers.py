def handle_create(payload: dict) -> dict:
    return {"action": "created", "data": payload}


def handle_update(payload: dict) -> dict:
    return {"action": "updated", "data": payload}


def handle_delete(payload: dict) -> dict:
    return {"action": "deleted", "data": payload}


HANDLER_MAP = {action: globals()[f"handle_{action}"] for action in ("create", "update", "delete")}


def dispatch(action: str, payload: dict) -> dict:
    handler = HANDLER_MAP.get(action)
    if handler is None:
        raise ValueError(f"Unknown action: {action}")
    return handler(payload)
