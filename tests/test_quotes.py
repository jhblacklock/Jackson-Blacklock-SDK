from urllib.parse import unquote

import responses as resp_lib
import pytest

from lotr_sdk import FilterCondition, FilterOptions, LotrNotFoundError
from tests.conftest import BASE_URL, SAMPLE_QUOTE, SAMPLE_QUOTE_2, paginated


@resp_lib.activate
def test_list_quotes(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/quote",
        json=paginated([SAMPLE_QUOTE, SAMPLE_QUOTE_2]),
        status=200,
    )
    result = client.quotes.list()

    assert result.total == 2
    assert len(result.docs) == 2

    quote = result.docs[0]
    assert quote.id == SAMPLE_QUOTE["_id"]
    assert quote.dialog == SAMPLE_QUOTE["dialog"]
    assert quote.movie_id == SAMPLE_QUOTE["movie"]
    assert quote.character_id == SAMPLE_QUOTE["character"]


@resp_lib.activate
def test_list_quotes_with_filter_match(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/quote",
        json=paginated([SAMPLE_QUOTE_2]),
        status=200,
    )
    client.quotes.list(FilterOptions(filters=[FilterCondition("dialog", "match", "precious")]))

    url = resp_lib.calls[0].request.url
    assert "dialog=/precious/i" in url


@resp_lib.activate
def test_list_quotes_with_pagination(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/quote",
        json=paginated([SAMPLE_QUOTE]),
        status=200,
    )
    client.quotes.list(FilterOptions(limit=10, page=3))

    url = resp_lib.calls[0].request.url
    assert "limit=10" in url
    assert "page=3" in url


@resp_lib.activate
def test_list_quotes_with_sort(client):
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/quote", json=paginated([SAMPLE_QUOTE]), status=200)
    client.quotes.list(FilterOptions(sort_by="dialog", sort_direction="asc"))
    url = resp_lib.calls[0].request.url
    assert "sort=dialog:asc" in url


@resp_lib.activate
def test_list_quotes_with_filter_eq(client):
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/quote", json=paginated([SAMPLE_QUOTE_2]), status=200)
    client.quotes.list(
        FilterOptions(filters=[FilterCondition("dialog", "eq", "My precious")])
    )
    url = unquote(resp_lib.calls[0].request.url)
    assert "dialog=My precious" in url


@resp_lib.activate
def test_list_quotes_with_filter_nin(client):
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/quote", json=paginated([SAMPLE_QUOTE]), status=200)
    movie_ids = [SAMPLE_QUOTE["movie"], "5cd95395de30eff6ebccde99"]
    client.quotes.list(FilterOptions(filters=[FilterCondition("movie", "nin", movie_ids)]))
    url = resp_lib.calls[0].request.url
    assert "movie!=" in url
    assert "5cd95395de30eff6ebccde56,5cd95395de30eff6ebccde99" in url


@resp_lib.activate
def test_get_quote_by_id(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/quote/{SAMPLE_QUOTE['_id']}",
        json=paginated([SAMPLE_QUOTE]),
        status=200,
    )
    quote = client.quotes.get(SAMPLE_QUOTE["_id"])

    assert quote.id == SAMPLE_QUOTE["_id"]
    assert quote.dialog == SAMPLE_QUOTE["dialog"]
    assert quote.movie_id == SAMPLE_QUOTE["movie"]
    assert quote.character_id == SAMPLE_QUOTE["character"]


@resp_lib.activate
def test_get_quote_not_found_empty_docs(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/quote/nonexistent",
        json=paginated([]),
        status=200,
    )
    with pytest.raises(LotrNotFoundError):
        client.quotes.get("nonexistent")


@resp_lib.activate
def test_get_quote_not_found_404(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/quote/nonexistent",
        json={"message": "Not found"},
        status=404,
    )
    with pytest.raises(LotrNotFoundError) as exc_info:
        client.quotes.get("nonexistent")
    assert exc_info.value.status_code == 404
