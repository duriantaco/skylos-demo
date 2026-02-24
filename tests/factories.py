from __future__ import annotations

import random
import string


class NoteFactory:
    _counter = 0

    @classmethod
    def create(cls, **overrides) -> dict:
        cls._counter += 1
        defaults = {
            "id": cls._counter,
            "title": f"Test Note {cls._counter}",
            "body": f"Body content for note {cls._counter}.",
        }
        defaults.update(overrides)
        return defaults

    @classmethod
    def create_batch(cls, count: int = 5, **overrides) -> list[dict]:
        return [cls.create(**overrides) for _ in range(count)]


class UserFactory:  # UNUSED (demo)
    _counter = 0

    @classmethod
    def create(cls, **overrides) -> dict:
        cls._counter += 1
        return {
            "id": cls._counter,
            "username": f"user_{cls._counter}",
            "email": f"user{cls._counter}@example.com",
            "role": overrides.get("role", "viewer"),
            **overrides,
        }


def random_email() -> str:  # UNUSED (demo)
    local = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{local}@test.example.com"


class TagFactory:  # UNUSED (demo)
    _counter = 0

    @classmethod
    def create(cls, **overrides) -> dict:
        cls._counter += 1
        return {"id": cls._counter, "name": f"tag-{cls._counter}", **overrides}
