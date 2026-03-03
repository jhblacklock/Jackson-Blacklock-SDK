import pytest

from lotr_sdk import LotrClient

BASE_URL = "https://the-one-api.dev/v2"

SAMPLE_MOVIE = {
    "_id": "5cd95395de30eff6ebccde56",
    "name": "The Lord of the Rings Series",
    "runtimeInMinutes": 558,
    "budgetInMillions": 281,
    "boxOfficeRevenueInMillions": 2917,
    "academyAwardNominations": 30,
    "academyAwardWins": 17,
    "rottenTomatoesScore": 94,
}

SAMPLE_MOVIE_2 = {
    "_id": "5cd95395de30eff6ebccde57",
    "name": "The Unexpected Journey",
    "runtimeInMinutes": 169,
    "budgetInMillions": 180,
    "boxOfficeRevenueInMillions": 1021,
    "academyAwardNominations": 3,
    "academyAwardWins": 1,
    "rottenTomatoesScore": 64,
}

SAMPLE_QUOTE = {
    "_id": "5cd96e05de30eff6ebcce7e9",
    "dialog": "Deagol!",
    "movie": "5cd95395de30eff6ebccde56",
    "character": "5cd99d4bde30eff6ebccfc15",
}

SAMPLE_QUOTE_2 = {
    "_id": "5cd96e05de30eff6ebcce7ea",
    "dialog": "My precious",
    "movie": "5cd95395de30eff6ebccde56",
    "character": "5cd99d4bde30eff6ebccfc16",
}


def paginated(docs: list, total: int | None = None) -> dict:
    """Helper to wrap docs in the standard API envelope."""
    return {
        "docs": docs,
        "total": total if total is not None else len(docs),
        "limit": 1000,
        "offset": 0,
        "page": 1,
        "pages": 1,
    }


@pytest.fixture
def client() -> LotrClient:
    return LotrClient(api_key="test-token", base_url=BASE_URL)
