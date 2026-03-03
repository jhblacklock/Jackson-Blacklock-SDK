"""Lord of the Rings API SDK.

Quick start::

    from lotr_sdk import LotrClient, FilterOptions, FilterCondition

    client = LotrClient(api_key="your-api-key")
    movies = client.movies.list()
    print(movies.docs[0].name)
"""

from lotr_sdk.client import LotrClient
from lotr_sdk.errors import LotrAuthError, LotrError, LotrNotFoundError, LotrRateLimitError
from lotr_sdk.filters import FilterCondition, FilterOperator, FilterOptions
from lotr_sdk.models import Movie, PaginatedResponse, Quote

__all__ = [
    "LotrClient",
    "FilterOptions",
    "FilterCondition",
    "FilterOperator",
    "Movie",
    "Quote",
    "PaginatedResponse",
    "LotrError",
    "LotrAuthError",
    "LotrNotFoundError",
    "LotrRateLimitError",
]
