from __future__ import annotations

from lotr_sdk.errors import LotrNotFoundError
from lotr_sdk.filters import FilterOptions
from lotr_sdk.models import Movie, PaginatedResponse, Quote
from lotr_sdk.resources.base import BaseResource


class MovieResource(BaseResource):
    def list(self, options: FilterOptions | None = None) -> PaginatedResponse[Movie]:
        """List all movies, with optional filtering/sorting/pagination."""
        data = self._get("/movie", options)
        return PaginatedResponse(
            docs=[Movie.from_dict(d) for d in data["docs"]],
            total=data["total"],
            limit=data["limit"],
            offset=data.get("offset", 0),
            page=data["page"],
            pages=data["pages"],
        )

    def get(self, movie_id: str) -> Movie:
        """Get a single movie by ID."""
        data = self._get(f"/movie/{movie_id}")
        if not data.get("docs"):
            raise LotrNotFoundError(f"Movie not found: {movie_id}", status_code=404)
        return Movie.from_dict(data["docs"][0])

    def get_quotes(
        self, movie_id: str, options: FilterOptions | None = None
    ) -> PaginatedResponse[Quote]:
        """Get all quotes for a specific movie."""
        data = self._get(f"/movie/{movie_id}/quote", options)
        return PaginatedResponse(
            docs=[Quote.from_dict(d) for d in data["docs"]],
            total=data["total"],
            limit=data["limit"],
            offset=data.get("offset", 0),
            page=data["page"],
            pages=data["pages"],
        )
