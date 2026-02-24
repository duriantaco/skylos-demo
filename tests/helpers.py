from __future__ import annotations

import time
from typing import Any

SLOW_TEST_THRESHOLD = 2.0  # UNUSED (demo)


def assert_json_response(response, status_code: int = 200) -> dict:
    assert response.status_code == status_code, (
        f"Expected {status_code}, got {response.status_code}: {response.text}"
    )
    return response.json()


def assert_paginated_response(response, min_items: int = 0) -> dict:  # UNUSED (demo)
    data = assert_json_response(response)
    assert "items" in data, "Missing 'items' key in paginated response"
    assert len(data["items"]) >= min_items
    return data


def create_test_note(client, title: str = "Test", body: str = "Body") -> dict:
    resp = client.post(
        "/notes/",
        json={"title": title, "body": body},
        headers={"X-API-Key": "dev-key"},
    )
    return assert_json_response(resp, 200)


def wait_for_event(event_name: str, timeout: float = 2.0) -> bool:  # UNUSED (demo)
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(0.05)
    return False


def mock_external_service(  # UNUSED (demo)
    base_url: str,
    responses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "base_url": base_url,
        "responses": responses or {},
        "call_count": 0,
    }
