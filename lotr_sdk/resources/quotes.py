from __future__ import annotations

from lotr_sdk.errors import LotrNotFoundError
from lotr_sdk.filters import FilterOptions
from lotr_sdk.models import PaginatedResponse, Quote
from lotr_sdk.resources.base import BaseResource


class QuoteResource(BaseResource):
    def list(self, options: FilterOptions | None = None) -> PaginatedResponse[Quote]:
        """List all quotes, with optional filtering/sorting/pagination."""
        data = self._get("/quote", options)
        return PaginatedResponse(
            docs=[Quote.from_dict(d) for d in data["docs"]],
            total=data["total"],
            limit=data["limit"],
            offset=data.get("offset", 0),
            page=data["page"],
            pages=data["pages"],
        )

    def get(self, quote_id: str) -> Quote:
        """Get a single quote by ID."""
        data = self._get(f"/quote/{quote_id}")
        if not data.get("docs"):
            raise LotrNotFoundError(f"Quote not found: {quote_id}", status_code=404)
        return Quote.from_dict(data["docs"][0])
