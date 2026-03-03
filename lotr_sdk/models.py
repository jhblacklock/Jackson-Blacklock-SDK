from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Movie:
    id: str
    name: str
    runtime_in_minutes: float
    budget_in_millions: float
    box_office_revenue_in_millions: float
    academy_award_nominations: int
    academy_award_wins: int
    rotten_tomatoes_score: float

    @classmethod
    def from_dict(cls, data: dict) -> "Movie":
        return cls(
            id=data["_id"],
            name=data["name"],
            runtime_in_minutes=data.get("runtimeInMinutes", 0.0),
            budget_in_millions=data.get("budgetInMillions", 0.0),
            box_office_revenue_in_millions=data.get("boxOfficeRevenueInMillions", 0.0),
            academy_award_nominations=data.get("academyAwardNominations", 0),
            academy_award_wins=data.get("academyAwardWins", 0),
            rotten_tomatoes_score=data.get("rottenTomatoesScore", 0.0),
        )


@dataclass(frozen=True)
class Quote:
    id: str
    dialog: str
    movie_id: str
    character_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "Quote":
        return cls(
            id=data["_id"],
            dialog=data.get("dialog", ""),
            movie_id=data.get("movie", ""),
            character_id=data.get("character", ""),
        )


@dataclass(frozen=True)
class PaginatedResponse(Generic[T]):
    docs: list
    total: int
    limit: int
    offset: int
    page: int
    pages: int
