from __future__ import annotations


class LotrError(Exception):
    """Base exception for all LOTR SDK errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class LotrAuthError(LotrError):
    """Raised when the API returns 401 Unauthorized."""


class LotrNotFoundError(LotrError):
    """Raised when the API returns 404 Not Found or docs list is empty for a single-item lookup."""


class LotrRateLimitError(LotrError):
    """Raised when the API returns 429 Too Many Requests (100 req / 10 min limit)."""
