from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

FilterOperator = Literal["eq", "ne", "gt", "gte", "lt", "lte", "match", "in", "nin", "exists"]


@dataclass
class FilterCondition:
    field: str
    operator: FilterOperator
    value: Any = None


@dataclass
class FilterOptions:
    limit: int | None = None
    page: int | None = None
    offset: int | None = None
    sort_by: str | None = None
    sort_direction: Literal["asc", "desc"] = "asc"
    filters: list[FilterCondition] = field(default_factory=list)


def build_query_string(options: FilterOptions) -> str:
    """Build a raw query string compatible with the mongoose-query-parser used by the LOTR API.

    The query string is appended raw to avoid percent-encoding operators like >, !=, etc.
    """
    parts: list[str] = []

    if options.limit is not None:
        parts.append(f"limit={options.limit}")
    if options.page is not None:
        parts.append(f"page={options.page}")
    if options.offset is not None:
        parts.append(f"offset={options.offset}")
    if options.sort_by:
        parts.append(f"sort={options.sort_by}:{options.sort_direction}")

    for condition in options.filters:
        f = condition.field
        v = condition.value
        op = condition.operator

        if op == "eq":
            parts.append(f"{f}={v}")
        elif op == "ne":
            parts.append(f"{f}!={v}")
        elif op == "gt":
            parts.append(f"{f}>{v}")
        elif op == "gte":
            parts.append(f"{f}>={v}")
        elif op == "lt":
            parts.append(f"{f}<{v}")
        elif op == "lte":
            parts.append(f"{f}<={v}")
        elif op == "match":
            parts.append(f"{f}=/{v}/i")
        elif op == "in":
            parts.append(f"{f}={','.join(str(x) for x in v)}")
        elif op == "nin":
            parts.append(f"{f}!={','.join(str(x) for x in v)}")
        elif op == "exists":
            parts.append(f if v else f"!{f}")

    return "&".join(parts)
