# LOTR SDK

A production-ready Python SDK for the [Lord of the Rings API](https://the-one-api.dev).

## Installation

```bash
pip install .
```

For development (includes pytest and the `responses` mock library):

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from lotr_sdk import LotrClient

client = LotrClient(api_key="your-api-key")
movies = client.movies.list()
print(movies.docs[0].name)  # "The Lord of the Rings Series"
```

## API Reference

### `LotrClient`

```python
LotrClient(api_key: str, base_url: str = "https://the-one-api.dev/v2", timeout: int = 10)
```

| Parameter  | Type  | Default                          | Description                       |
|------------|-------|----------------------------------|-----------------------------------|
| `api_key`  | `str` | —                                | Bearer token from the-one-api.dev |
| `base_url` | `str` | `https://the-one-api.dev/v2`     | Override for testing              |
| `timeout`  | `int` | `10`                             | Request timeout in seconds        |

---

### `client.movies`

#### `list(options=None) -> PaginatedResponse[Movie]`

List all movies. Supports filtering, sorting, and pagination.

```python
movies = client.movies.list()
# With options:
from lotr_sdk import FilterOptions, FilterCondition

movies = client.movies.list(FilterOptions(
    limit=5,
    page=1,
    sort_by="academyAwardWins",
    sort_direction="desc",
    filters=[FilterCondition("academyAwardWins", "gt", 2)],
))
```

#### `get(movie_id: str) -> Movie`

Get a single movie by its ID. Raises `LotrNotFoundError` if not found.

```python
movie = client.movies.get("5cd95395de30eff6ebccde56")
print(movie.name)
```

#### `get_quotes(movie_id: str, options=None) -> PaginatedResponse[Quote]`

Get all quotes for a specific movie.

```python
quotes = client.movies.get_quotes(movie.id, FilterOptions(limit=10))
for quote in quotes.docs:
    print(quote.dialog)
```

---

### `client.quotes`

#### `list(options=None) -> PaginatedResponse[Quote]`

List all quotes. Supports filtering, sorting, and pagination.

```python
quotes = client.quotes.list(FilterOptions(
    filters=[FilterCondition("dialog", "match", "precious")],
    limit=5,
))
```

#### `get(quote_id: str) -> Quote`

Get a single quote by its ID. Raises `LotrNotFoundError` if not found.

```python
quote = client.quotes.get("5cd96e05de30eff6ebcce7e9")
print(quote.dialog)
```

---

### Models

#### `Movie`

| Field                          | Type    | Description                  |
|-------------------------------|---------|------------------------------|
| `id`                          | `str`   | MongoDB ObjectId             |
| `name`                        | `str`   | Movie title                  |
| `runtime_in_minutes`          | `float` | Runtime in minutes           |
| `budget_in_millions`          | `float` | Budget in millions USD       |
| `box_office_revenue_in_millions` | `float` | Box office revenue          |
| `academy_award_nominations`   | `int`   | Number of nominations        |
| `academy_award_wins`          | `int`   | Number of wins               |
| `rotten_tomatoes_score`       | `float` | Rotten Tomatoes score (0-100)|

#### `Quote`

| Field          | Type  | Description                  |
|---------------|-------|------------------------------|
| `id`          | `str` | MongoDB ObjectId             |
| `dialog`      | `str` | The quote text               |
| `movie_id`    | `str` | ObjectId of the movie        |
| `character_id`| `str` | ObjectId of the character    |

#### `PaginatedResponse[T]`

| Field    | Type      | Description                        |
|---------|-----------|------------------------------------|
| `docs`  | `list[T]` | The items for this page            |
| `total` | `int`     | Total number of items              |
| `limit` | `int`     | Items per page                     |
| `offset`| `int`     | Item offset                        |
| `page`  | `int`     | Current page number                |
| `pages` | `int`     | Total number of pages              |

---

### Filtering

Use `FilterOptions` and `FilterCondition` to build queries.

```python
FilterCondition(field: str, operator: FilterOperator, value: Any = None)
```

#### Supported Operators

| Operator  | Description           | Example                                              |
|-----------|-----------------------|------------------------------------------------------|
| `"eq"`    | Equals                | `FilterCondition("name", "eq", "Fellowship")`        |
| `"ne"`    | Not equals            | `FilterCondition("academyAwardWins", "ne", 0)`       |
| `"gt"`    | Greater than          | `FilterCondition("academyAwardWins", "gt", 2)`       |
| `"gte"`   | Greater than or equal | `FilterCondition("runtimeInMinutes", "gte", 180)`    |
| `"lt"`    | Less than             | `FilterCondition("budgetInMillions", "lt", 100)`     |
| `"lte"`   | Less than or equal    | `FilterCondition("rottenTomatoesScore", "lte", 50)`  |
| `"match"` | Regex match (case-insensitive) | `FilterCondition("dialog", "match", "ring")` |
| `"in"`    | In a list of values   | `FilterCondition("academyAwardWins", "in", [1,2,3])` |
| `"nin"`   | Not in a list         | `FilterCondition("academyAwardWins", "nin", [0])`    |
| `"exists"`| Field exists / not exists | `FilterCondition("budget", "exists", True)`      |

#### `FilterOptions`

```python
FilterOptions(
    limit: int | None = None,       # Items per page
    page: int | None = None,        # Page number (1-based)
    offset: int | None = None,      # Item offset
    sort_by: str | None = None,     # Field to sort by (use API field names)
    sort_direction: "asc" | "desc" = "asc",
    filters: list[FilterCondition] = [],
)
```

**Note on `sort_by` field names:** Use the raw API field names (camelCase) when sorting, e.g., `"academyAwardWins"`, `"runtimeInMinutes"`. Filtering field names also use the API's camelCase names.

---

### Error Handling

```python
from lotr_sdk import LotrAuthError, LotrNotFoundError, LotrRateLimitError, LotrError

try:
    movie = client.movies.get("bad-id")
except LotrNotFoundError:
    print("Movie not found")
except LotrAuthError:
    print("Invalid API key")
except LotrRateLimitError:
    print("Rate limit hit — 100 req / 10 min")
except LotrError as e:
    print(f"API error {e.status_code}: {e}")
```

| Exception           | HTTP Status | When raised                          |
|--------------------|-------------|--------------------------------------|
| `LotrAuthError`    | 401         | Invalid or missing API key           |
| `LotrNotFoundError`| 404 / empty | Resource not found                   |
| `LotrRateLimitError`| 429        | Rate limit exceeded (100 req/10 min) |
| `LotrError`        | Other       | Any other API error                  |

---

## Running Tests

```bash
cd lotr-sdk
pip install -e ".[dev]"
pytest --cov=lotr_sdk
```

## Running the Demo

Get a free API key at [the-one-api.dev](https://the-one-api.dev), then:

```bash
cd lotr-sdk
LOTR_API_KEY=<your-api-key> python examples/demo.py
```
