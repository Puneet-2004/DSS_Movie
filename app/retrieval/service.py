from app.conversation.schema import UserPreferences

from app.retrieval.models import (
    RetrievalMetadata,
    RetrievalQuery,
    RetrievalResult,
)

from app.retrieval.movie_fetcher import MovieFetcher

from app.retrieval.tmdb_fetcher import TMDBFetcher

from app.retrieval.normalizer import normalize_candidate


class MovieRetrievalService:

    def __init__(self):

        self.tmdb_fetcher = TMDBFetcher()

        self.local_fetcher = MovieFetcher()

    def build_query(
        self,
        preferences: UserPreferences
    ) -> RetrievalQuery:

        if not preferences.location:
            raise ValueError(
                "Location is required before retrieval."
            )

        if not preferences.preferred_date:
            raise ValueError(
                "Preferred date is required before retrieval."
            )

        return RetrievalQuery(
            location=preferences.location,

            preferred_date=preferences.preferred_date,

            budget=preferences.budget,

            max_travel_distance_km=preferences.max_travel_distance_km,

            preferred_genres=preferences.preferred_genres or [],

            preferred_languages=preferences.preferred_languages or [],

            preferred_time_range=preferences.preferred_time_range,

            wants_food=preferences.wants_food,

            preferred_formats=preferences.preferred_formats or [],

            selected_movie_title=preferences.selected_movie_title,
        )

    def determine_retrieval_strategy(
        self,
        query: RetrievalQuery
    ) -> str:

        if query.selected_movie_title:
            return "fixed_movie"

        return "open_recommendation"

    def retrieve(
        self,
        preferences: UserPreferences
    ) -> RetrievalResult:

        query = self.build_query(preferences)

        retrieval_strategy = self.determine_retrieval_strategy(
            query
        )

        source_notes = []

        raw_candidates = []

        fetcher_used = "unknown"

        try:

            raw_candidates = self.tmdb_fetcher.fetch(
                query
            )

            fetcher_used = "TMDb"

            source_notes.append(
                "Primary provider: TMDb"
            )

        except Exception as exc:

            print("\nTMDb FAILED")
            print(str(exc))

            source_notes.append(
                f"TMDb failed: {str(exc)}"
            )

            raw_candidates = self.local_fetcher.fetch(
                query
            )

            fetcher_used = "LocalFallback"

            source_notes.append(
                "Fallback provider: Local sample data"
            )

        candidates = []

        for item in raw_candidates:

            candidate = normalize_candidate(item)

            candidate.retrieval_strategy = retrieval_strategy

            candidates.append(candidate)

        metadata = RetrievalMetadata(
            retrieval_strategy=retrieval_strategy,

            candidate_count=len(candidates),

            selected_movie_title=query.selected_movie_title,
        )

        source_notes.append(
            f"Fetcher used: {fetcher_used}"
        )

        return RetrievalResult(
            query=query,

            metadata=metadata,

            candidates=candidates,

            source_notes=source_notes,
        )