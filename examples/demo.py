#!/usr/bin/env python3
"""LOTR SDK demo — requires a valid API key.

Usage (from the lotr-sdk directory):
    LOTR_API_KEY=<your-key> python examples/demo.py
"""

import os
import sys

from lotr_sdk import FilterCondition, FilterOptions, LotrClient


def main() -> None:
    api_key = os.environ.get("LOTR_API_KEY")
    if not api_key:
        print("Error: LOTR_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = LotrClient(api_key=api_key)

    # 1. List all movies
    print("=== All Movies ===")
    movies = client.movies.list()
    print(f"Found {movies.total} movies:")
    for movie in movies.docs:
        print(f"  [{movie.id}] {movie.name} ({movie.runtime_in_minutes} min)")

    # 2. Movies with more than 2 Academy Award wins
    #
    # NOTE: sort is intentionally omitted here. The live API returns HTTP 500
    # for any ?sort= parameter due to missing CosmosDB indexes in production.
    # This is a known server-side bug: https://github.com/gitfrosh/lotr-api/issues/188
    # The SDK's sort implementation is correct — the server simply can't fulfill it.
    print("\n=== Award Winners (>2 wins) ===")
    award_winners = client.movies.list(
        FilterOptions(
            filters=[FilterCondition("academyAwardWins", "gt", 2)],
        )
    )
    for movie in award_winners.docs:
        print(f"  {movie.name}: {movie.academy_award_wins} wins")

    # 3. Get a specific movie by ID — use The Return of the King, which has quotes.
    #    (The first entry "The Lord of the Rings Series" is a grouped record with no quotes.)
    rotk_id = "5cd95395de30eff6ebccde5d"
    print(f"\n=== Single Movie Lookup ===")
    movie = client.movies.get(rotk_id)
    print(f"  {movie.name}")
    print(f"  Budget: ${movie.budget_in_millions}M")
    print(f"  Box office: ${movie.box_office_revenue_in_millions}M")
    print(f"  Academy Awards: {movie.academy_award_wins} wins / {movie.academy_award_nominations} nominations")
    print(f"  Rotten Tomatoes: {movie.rotten_tomatoes_score}%")

    # 4. Get quotes for that movie (first 5)
    print(f"\n=== First 5 Quotes from '{movie.name}' ===")
    quotes = client.movies.get_quotes(movie.id, FilterOptions(limit=5))
    print(f"  (Total quotes for this movie: {quotes.total})")
    for quote in quotes.docs:
        print(f"  \"{quote.dialog}\"")

    # 5. Search quotes matching "ring"
    print('\n=== Quotes Matching "ring" (first 5) ===')
    ring_quotes = client.quotes.list(
        FilterOptions(
            filters=[FilterCondition("dialog", "match", "ring")],
            limit=5,
        )
    )
    print(f"Total matching: {ring_quotes.total}")
    for quote in ring_quotes.docs:
        print(f"  \"{quote.dialog}\"")

    # 6. List all quotes (paginated)
    print("\n=== All Quotes (page 1, limit 3) ===")
    all_quotes = client.quotes.list(FilterOptions(limit=3, page=1))
    print(f"Showing {len(all_quotes.docs)} of {all_quotes.total} total quotes (page {all_quotes.page}/{all_quotes.pages})")
    for quote in all_quotes.docs:
        print(f"  \"{quote.dialog}\"")

    # 7. Get a single quote by ID
    print("\n=== Single Quote Lookup ===")
    quote = client.quotes.get(quotes.docs[0].id)
    print(f"  \"{quote.dialog}\"")
    print(f"  movie_id={quote.movie_id}, character_id={quote.character_id}")


if __name__ == "__main__":
    main()
