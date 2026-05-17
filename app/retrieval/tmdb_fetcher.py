from typing import Any, Dict, List

from app.retrieval.models import RetrievalQuery
from app.retrieval.tmdb_client import TMDBClient


class TMDBFetcher:

    def __init__(self):

        self.client = TMDBClient()

    def fetch(
        self,
        query: RetrievalQuery
    ) -> List[Dict[str, Any]]:

        search_query = self._build_search_query(query)

        results = self.client.search_movies(
            search_query
        )

        normalized = []

        for movie in results.get("results", [])[:10]:

            normalized.append(
                {
                    "movie_title":
                        movie.get("title"),

                    "theater_name":
                        "Local Theater Placeholder",

                    "showtime":
                        "07:00 PM",

                    "ticket_price":
                        300,

                    "location":
                        query.location,

                    "distance_km":
                        5.0,

                    "language":
                        movie.get("original_language"),

                    "genres":
                        [],

                    "amenities":
                        ["Food Court"],

                    "source_name":
                        "tmdb",

                    "source_url":
                        f"https://www.themoviedb.org/movie/{movie.get('id')}",

                    "tmdb_id":
                        movie.get("id"),

                    "overview":
                        movie.get("overview"),

                    "rating":
                        movie.get("vote_average"),

                    "popularity":
                        movie.get("popularity"),
                }
            )

        return normalized

    def _build_search_query(
        self,
        query: RetrievalQuery
    ) -> str:

        if query.selected_movie_title:
            return query.selected_movie_title

        if query.preferred_genres:
            return query.preferred_genres[0]

        return "popular"    