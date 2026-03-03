from __future__ import annotations

import requests

from lotr_sdk.errors import LotrAuthError, LotrError, LotrNotFoundError, LotrRateLimitError
from lotr_sdk.filters import FilterOptions, build_query_string


class BaseResource:
    def __init__(self, session: requests.Session, base_url: str, timeout: int = 10) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _get(self, path: str, options: FilterOptions | None = None) -> dict:
        url = f"{self._base_url}{path}"
        if options:
            qs = build_query_string(options)
            if qs:
                url = f"{url}?{qs}"
        # Use PreparedRequest so session headers (auth) are merged, then restore
        # the raw URL to prevent requests from percent-encoding filter operators
        # like > and < which the API's query parser requires as literal characters.
        prepared = self._session.prepare_request(requests.Request("GET", url))
        prepared.url = url
        resp = self._session.send(prepared, timeout=self._timeout)
        self._raise_for_status(resp)
        return resp.json()

    def _raise_for_status(self, resp: requests.Response) -> None:
        if resp.ok:
            return
        try:
            detail = resp.json().get("message", resp.text)
        except Exception:
            detail = resp.text

        if resp.status_code == 401:
            raise LotrAuthError(f"Authentication failed: {detail}", status_code=401)
        if resp.status_code == 404:
            raise LotrNotFoundError(f"Resource not found: {detail}", status_code=404)
        if resp.status_code == 429:
            raise LotrRateLimitError(
                f"Rate limit exceeded (100 req / 10 min): {detail}", status_code=429
            )
        raise LotrError(f"API error {resp.status_code}: {detail}", status_code=resp.status_code)
