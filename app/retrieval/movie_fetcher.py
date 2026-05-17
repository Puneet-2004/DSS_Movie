from datetime import datetime
from typing import Any, Dict, List, Optional

from app.retrieval.base import BaseMovieFetcher
from app.retrieval.models import RetrievalQuery


class MovieFetcher(BaseMovieFetcher):
    def __init__(self):
        self.sample_data: List[Dict[str, Any]] = [
            {
                "movie_title": "Mission Impossible: Dead Reckoning",
                "theater_name": "PVR Nexus, Koramangala",
                "showtime": "07:20 PM",
                "ticket_price": 280,
                "location": "Bangalore",
                "distance_km": 4.2,
                "language": "English",
                "genres": ["Action", "Thriller"],
                "amenities": ["Food Court", "Parking"],
                "source_name": "local_sample",
                "source_url": "local://sample/1",
            },
            {
                "movie_title": "Inside Out 2",
                "theater_name": "INOX Garuda Mall",
                "showtime": "06:10 PM",
                "ticket_price": 220,
                "location": "Bangalore",
                "distance_km": 6.0,
                "language": "English",
                "genres": ["Animation", "Comedy"],
                "amenities": ["Food Court", "Parking"],
                "source_name": "local_sample",
                "source_url": "local://sample/2",
            },
            {
                "movie_title": "Kalki 2898 AD",
                "theater_name": "Cinepolis Bannerghatta",
                "showtime": "09:00 PM",
                "ticket_price": 350,
                "location": "Bangalore",
                "distance_km": 9.5,
                "language": "Telugu",
                "genres": ["Action", "Sci-Fi"],
                "amenities": ["Food Court"],
                "source_name": "local_sample",
                "source_url": "local://sample/3",
            },
            {
                "movie_title": "A Quiet Place: Day One",
                "theater_name": "PVR Orion Mall",
                "showtime": "03:30 PM",
                "ticket_price": 250,
                "location": "Bangalore",
                "distance_km": 11.0,
                "language": "English",
                "genres": ["Horror", "Thriller"],
                "amenities": ["Parking"],
                "source_name": "local_sample",
                "source_url": "local://sample/4",
            },
        ]

    def fetch(self, query: RetrievalQuery) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        for item in self.sample_data:
            if query.selected_movie_title:
                if not self._matches_movie_title(query.selected_movie_title, item):
                    continue

            if not self._matches_location(query.location, item):
                continue

            if query.budget is not None:
                price = item.get("ticket_price")
                if price is not None and price > query.budget:
                    continue

            if query.max_travel_distance_km is not None:
                distance = item.get("distance_km")
                if distance is not None and distance > query.max_travel_distance_km:
                    continue

            if query.preferred_genres and not self._matches_any(
                item.get("genres", []), query.preferred_genres
            ):
                continue

            if query.preferred_languages and not self._matches_any(
                [item.get("language", "")], query.preferred_languages
            ):
                continue

            if query.preferred_time_range and not self._matches_time_range(
                item.get("showtime", ""), query.preferred_time_range
            ):
                continue

            results.append(item)

        return results

    def _matches_movie_title(self, selected_title: str, item: Dict[str, Any]) -> bool:
        selected_title = selected_title.strip().lower()
        movie_title = str(item.get("movie_title", "")).strip().lower()
        return selected_title in movie_title or movie_title in selected_title

    def _matches_location(self, user_location: str, item: Dict[str, Any]) -> bool:
        user_location = (user_location or "").strip().lower()
        item_location = (item.get("location") or "").strip().lower()
        theater_name = (item.get("theater_name") or "").strip().lower()

        if not user_location:
            return True

        return user_location in item_location or user_location in theater_name or "bangalore" in user_location

    def _matches_any(self, source_values: List[str], preferred_values: List[str]) -> bool:
        source_normalized = {str(v).strip().lower() for v in source_values if v is not None}
        preferred_normalized = [str(v).strip().lower() for v in preferred_values if v is not None]

        return any(value in source_normalized for value in preferred_normalized)

    def _matches_time_range(self, showtime: str, preferred_time_range: str) -> bool:
        hour = self._parse_hour(showtime)
        if hour is None:
            return True

        preferred_time_range = (preferred_time_range or "").strip().lower()

        if preferred_time_range == "morning":
            return 5 <= hour < 12
        if preferred_time_range == "afternoon":
            return 12 <= hour < 17
        if preferred_time_range == "evening":
            return 17 <= hour < 20
        if preferred_time_range == "night":
            return 20 <= hour <= 23

        return True

    def _parse_hour(self, showtime: str) -> Optional[int]:
        try:
            dt = datetime.strptime(showtime.strip().upper(), "%I:%M %p")
            return dt.hour
        except ValueError:
            return None