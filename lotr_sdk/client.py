from __future__ import annotations

import requests

from lotr_sdk.resources.movies import MovieResource
from lotr_sdk.resources.quotes import QuoteResource


class LotrClient:
    """Main entry point for the LOTR SDK.

    Usage::

        client = LotrClient(api_key="your-api-key")
        movies = client.movies.list()
        quotes = client.quotes.list()
    """

    movies: MovieResource
    quotes: QuoteResource

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://the-one-api.dev/v2",
        timeout: int = 10,
    ) -> None:
        session = requests.Session()
        session.headers["Authorization"] = f"Bearer {api_key}"
        session.headers["Accept"] = "application/json"

        self.movies = MovieResource(session, base_url, timeout=timeout)
        self.quotes = QuoteResource(session, base_url, timeout=timeout)
