# LOTR SDK — Design Document

## Architecture Overview

```
LotrClient
├── movies: MovieResource
└── quotes: QuoteResource
         └── (both inherit) BaseResource
                              ├── _get(path, options) → dict
                              └── _raise_for_status(resp)
```

The SDK has three distinct layers:

1. **Client layer** (`LotrClient`) — user-facing entry point. Owns the `requests.Session` and injects auth/timeout. Exposes typed resource attributes.

2. **Resource layer** (`MovieResource`, `QuoteResource`) — domain-specific methods with typed return values. Converts raw dicts to model dataclasses.

3. **HTTP layer** (`BaseResource`) — shared HTTP logic: URL construction, raw query string appending, error mapping.

---

## Key Decisions

### 1. Raw query string appended to URL (not `params=`)

The LOTR API uses a mongoose-query-parser that requires operators like `>`, `>=`, `!=` to appear literally in the URL. If these were passed through `requests`'s `params=` dict, they would be percent-encoded (`%3E`, `%21%3D`), breaking the filter syntax.

**Solution:** `build_query_string()` assembles a raw string that is appended directly to the URL with `?`.

```python
url = f"{url}?{qs}"   # raw, not params=
```

### 2. Frozen dataclasses for models

`Movie`, `Quote`, and `PaginatedResponse` are `frozen=True` dataclasses. This makes them:
- **Immutable** — callers cannot accidentally mutate API response data.
- **Hashable** — can be used in sets/dicts.
- **Serialization-friendly** — easy to convert to dict with `dataclasses.asdict()`.

### 3. snake_case renaming (Pythonic field names)

The API returns camelCase JSON (`runtimeInMinutes`, `academyAwardWins`). The SDK translates these to snake_case (`runtime_in_minutes`, `academy_award_wins`) in each model's `from_dict()` classmethod, following Python convention.

The `_id` MongoDB field is mapped to `id`.

### 4. Error hierarchy

```
Exception
└── LotrError(message, status_code)
    ├── LotrAuthError       (401)
    ├── LotrNotFoundError   (404, or empty docs on single-item lookup)
    └── LotrRateLimitError  (429)
```

All errors carry `status_code` for programmatic handling. The hierarchy lets callers catch broadly (`LotrError`) or specifically (`LotrAuthError`).

`LotrNotFoundError` is also raised when the API returns 200 with an empty `docs` array for a single-item `get()` call — this matches the actual API behavior for some IDs.

### 5. Timeout via `session.send` wrapping

`requests.Session` does not have a global timeout setting. Instead of requiring callers to pass `timeout=` per-request (which `BaseResource._get` would need to thread through), we wrap `session.send` at construction time to inject the default, preserving it for all requests transparently.

### 6. `FilterOptions` as a single configuration object

Rather than accepting `limit`, `page`, `sort_by`, and `filters` as separate keyword arguments on every method, all query configuration is bundled in `FilterOptions`. Benefits:
- Methods stay clean (`list(options)` vs `list(limit=..., page=..., sort_by=..., filters=...)`).
- Easy to construct, store, and reuse filter configurations.
- Extensible: new query params can be added to `FilterOptions` without changing method signatures.

---

## Extensibility: Adding New Resources

To add a new resource (e.g., `CharacterResource`):

1. Create `lotr_sdk/resources/characters.py`:

```python
from lotr_sdk.resources.base import BaseResource
from lotr_sdk.filters import FilterOptions
from lotr_sdk.models import PaginatedResponse

@dataclass(frozen=True)
class Character:
    id: str
    name: str
    # ...

    @classmethod
    def from_dict(cls, data: dict) -> "Character": ...

class CharacterResource(BaseResource):
    def list(self, options: FilterOptions | None = None) -> PaginatedResponse[Character]:
        data = self._get("/character", options)
        return PaginatedResponse(
            docs=[Character.from_dict(d) for d in data["docs"]],
            **{k: data[k] for k in ("total", "limit", "offset", "page", "pages")},
        )

    def get(self, character_id: str) -> Character:
        data = self._get(f"/character/{character_id}")
        if not data.get("docs"):
            raise LotrNotFoundError(f"Character not found: {character_id}")
        return Character.from_dict(data["docs"][0])
```

2. Add `self.characters = CharacterResource(session, base_url)` to `LotrClient.__init__`.
3. Export from `lotr_sdk/__init__.py`.
4. Add tests in `tests/test_characters.py`.

No changes to `BaseResource` or the filter system are needed.

---

## Trade-offs Considered

| Decision | Alternative | Why we chose this |
|---|---|---|
| `responses` library for tests | `unittest.mock` / `httpretty` | `responses` integrates cleanly with `requests`, has good assertion support, and is well-maintained |
| Dataclasses over Pydantic | Pydantic v2 | Avoids a heavy dependency; dataclasses are stdlib and sufficient for read-only API responses |
| `FilterOptions` dataclass | Dict kwargs | Type-safe, discoverable, reusable; IDE autocomplete works |
| Raw query string | `params=` dict | Required to preserve filter operators that urllib would encode |
| `session.send` wrapping for timeout | Per-request `timeout` param | Transparent; callers don't need to know about it |
| `from_dict()` classmethods | `dacite` / `cattrs` | No extra deps; the mapping logic is simple and explicit |
