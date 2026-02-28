from __future__ import annotations

from tests.helpers import assert_json_response, create_test_note


def test_create_note(test_client, api_key_header):
    resp = test_client.post(
        "/notes/",
        json={"title": "Hello", "body": "World"},
        headers=api_key_header,
    )
    data = assert_json_response(resp, 200)
    assert data["title"] == "Hello"
    assert data["body"] == "World"


def _seed_notes(
    client, count: int = 3, api_key_header: dict | None = None
) -> list[dict]:  # UNUSED (demo)
    headers = api_key_header or {"X-API-Key": "dev-key"}
    return [create_test_note(client, title=f"Note {i}", body=f"Body {i}") for i in range(count)]


def test_list_notes(test_client, api_key_header):
    create_test_note(test_client, title="List me", body="Content")
    resp = test_client.get("/notes/", headers=api_key_header)
    data = assert_json_response(resp)
    assert isinstance(data, list)


def test_create_note_with_tags(test_client, api_key_header):  # UNUSED (demo)
    resp = test_client.post(
        "/notes/",
        json={"title": "Tagged", "body": "Content", "tags": ["python", "demo"]},
        headers=api_key_header,
    )
    data = assert_json_response(resp, 200)
    assert "tags" in data


def test_search_notes(test_client, api_key_header):
    create_test_note(test_client, title="Searchable", body="Find me")
    resp = test_client.get("/notes/search?q=Searchable", headers=api_key_header)
    data = assert_json_response(resp)
    assert isinstance(data, list)


def test_bulk_import_notes(test_client, api_key_header):  # UNUSED (demo)
    notes = [{"title": f"Import {i}", "body": f"Body {i}"} for i in range(5)]
    resp = test_client.post(
        "/notes/import",
        json=notes,
        headers=api_key_header,
    )
    data = assert_json_response(resp, 200)
    assert data.get("imported") == 5
