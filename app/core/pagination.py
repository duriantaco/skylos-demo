from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, Sequence

T = TypeVar("T")


@dataclass
class PageParams:
    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


@dataclass
class PageResult(Generic[T]):
    items: list[T] = field(default_factory=list)
    total: int = 0
    page: int = 1
    size: int = 20

    @property
    def pages(self) -> int:
        return (self.total + self.size - 1) // self.size if self.size else 0

@dataclass
class CursorParams:  # UNUSED (demo)
    cursor: str | None = None
    limit: int = 20


@dataclass
class CursorResult(Generic[T]):  # UNUSED (demo)
    items: list[T] = field(default_factory=list)
    next_cursor: str | None = None
    has_more: bool = False


def paginate(items: Sequence[T], params: PageParams) -> PageResult[T]:
    total = len(items)
    start = params.offset
    end = start + params.size
    return PageResult(
        items=list(items[start:end]),
        total=total,
        page=params.page,
        size=params.size,
    )


def apply_filters(items: Sequence[Any], filters: dict[str, Any]) -> list[Any]:  # UNUSED (demo)
    result = list(items)
    for key, value in filters.items():
        result = [item for item in result if getattr(item, key, None) == value]
    return result
