from urllib.parse import unquote

import responses as resp_lib
import pytest

from lotr_sdk import FilterCondition, FilterOptions, LotrNotFoundError
from tests.conftest import (
    BASE_URL,
    SAMPLE_MOVIE,
    SAMPLE_MOVIE_2,
    SAMPLE_QUOTE,
    SAMPLE_QUOTE_2,
    paginated,
)


@resp_lib.activate
def test_list_movies(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json=paginated([SAMPLE_MOVIE, SAMPLE_MOVIE_2]),
        status=200,
    )
    result = client.movies.list()

    assert result.total == 2
    assert result.limit == 1000
    assert result.offset == 0
    assert result.page == 1
    assert result.pages == 1
    assert len(result.docs) == 2

    movie = result.docs[0]
    assert movie.id == SAMPLE_MOVIE["_id"]
    assert movie.name == SAMPLE_MOVIE["name"]
    assert movie.runtime_in_minutes == SAMPLE_MOVIE["runtimeInMinutes"]
    assert movie.budget_in_millions == SAMPLE_MOVIE["budgetInMillions"]
    assert movie.box_office_revenue_in_millions == SAMPLE_MOVIE["boxOfficeRevenueInMillions"]
    assert movie.academy_award_nominations == SAMPLE_MOVIE["academyAwardNominations"]
    assert movie.academy_award_wins == SAMPLE_MOVIE["academyAwardWins"]
    assert movie.rotten_tomatoes_score == SAMPLE_MOVIE["rottenTomatoesScore"]


@resp_lib.activate
def test_list_movies_with_pagination(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json=paginated([SAMPLE_MOVIE]),
        status=200,
    )
    client.movies.list(FilterOptions(limit=5, page=2, offset=5))

    url = resp_lib.calls[0].request.url
    assert "limit=5" in url
    assert "page=2" in url
    assert "offset=5" in url


@resp_lib.activate
def test_list_movies_with_sort(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json=paginated([SAMPLE_MOVIE_2, SAMPLE_MOVIE]),
        status=200,
    )
    client.movies.list(FilterOptions(sort_by="academyAwardWins", sort_direction="desc"))

    url = resp_lib.calls[0].request.url
    assert "sort=academyAwardWins:desc" in url


@resp_lib.activate
def test_list_movies_with_filter_gt(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json=paginated([SAMPLE_MOVIE]),
        status=200,
    )
    client.movies.list(
        FilterOptions(filters=[FilterCondition("academyAwardWins", "gt", 2)])
    )

    url = unquote(resp_lib.calls[0].request.url)
    assert "academyAwardWins>2" in url


@resp_lib.activate
def test_list_movies_with_filter_eq(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json=paginated([SAMPLE_MOVIE]),
        status=200,
    )
    client.movies.list(
        FilterOptions(filters=[FilterCondition("name", "eq", "The Fellowship of the Ring")])
    )

    url = unquote(resp_lib.calls[0].request.url)
    assert "name=The Fellowship of the Ring" in url


@resp_lib.activate
def test_list_movies_with_filter_ne(client):
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/movie", json=paginated([SAMPLE_MOVIE]), status=200)
    client.movies.list(FilterOptions(filters=[FilterCondition("academyAwardWins", "ne", 0)]))
    url = resp_lib.calls[0].request.url
    assert "academyAwardWins!=0" in url


@resp_lib.activate
def test_list_movies_with_filter_in(client):
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/movie", json=paginated([SAMPLE_MOVIE]), status=200)
    client.movies.list(
        FilterOptions(filters=[FilterCondition("academyAwardWins", "in", [1, 2, 3])])
    )
    url = resp_lib.calls[0].request.url
    assert "academyAwardWins=1,2,3" in url


@resp_lib.activate
def test_list_movies_with_filter_match(client):
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/movie", json=paginated([SAMPLE_MOVIE]), status=200)
    client.movies.list(FilterOptions(filters=[FilterCondition("name", "match", "ring")]))
    url = resp_lib.calls[0].request.url
    assert "name=/ring/i" in url


@resp_lib.activate
def test_list_movies_with_filter_exists(client):
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/movie", json=paginated([SAMPLE_MOVIE]), status=200)
    client.movies.list(FilterOptions(filters=[FilterCondition("budgetInMillions", "exists", True)]))
    url = resp_lib.calls[0].request.url
    assert "budgetInMillions" in url
    assert "!budgetInMillions" not in url


@resp_lib.activate
def test_list_movies_with_filter_not_exists(client):
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/movie", json=paginated([SAMPLE_MOVIE]), status=200)
    client.movies.list(FilterOptions(filters=[FilterCondition("budgetInMillions", "exists", False)]))
    url = resp_lib.calls[0].request.url
    assert "!budgetInMillions" in url


@resp_lib.activate
def test_get_movie_by_id(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie/{SAMPLE_MOVIE['_id']}",
        json=paginated([SAMPLE_MOVIE]),
        status=200,
    )
    movie = client.movies.get(SAMPLE_MOVIE["_id"])

    assert movie.id == SAMPLE_MOVIE["_id"]
    assert movie.name == SAMPLE_MOVIE["name"]


@resp_lib.activate
def test_get_movie_not_found_empty_docs(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie/nonexistent",
        json=paginated([]),
        status=200,
    )
    with pytest.raises(LotrNotFoundError):
        client.movies.get("nonexistent")


@resp_lib.activate
def test_get_movie_not_found_404(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie/nonexistent",
        json={"message": "Not found"},
        status=404,
    )
    with pytest.raises(LotrNotFoundError) as exc_info:
        client.movies.get("nonexistent")
    assert exc_info.value.status_code == 404


@resp_lib.activate
def test_get_movie_quotes(client):
    movie_id = SAMPLE_MOVIE["_id"]
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie/{movie_id}/quote",
        json=paginated([SAMPLE_QUOTE, SAMPLE_QUOTE_2], total=2),
        status=200,
    )
    result = client.movies.get_quotes(movie_id)

    assert result.total == 2
    assert len(result.docs) == 2

    quote = result.docs[0]
    assert quote.id == SAMPLE_QUOTE["_id"]
    assert quote.dialog == SAMPLE_QUOTE["dialog"]
    assert quote.movie_id == SAMPLE_QUOTE["movie"]
    assert quote.character_id == SAMPLE_QUOTE["character"]


@resp_lib.activate
def test_get_movie_quotes_with_limit(client):
    movie_id = SAMPLE_MOVIE["_id"]
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie/{movie_id}/quote",
        json=paginated([SAMPLE_QUOTE]),
        status=200,
    )
    client.movies.get_quotes(movie_id, FilterOptions(limit=1))

    url = resp_lib.calls[0].request.url
    assert "limit=1" in url
