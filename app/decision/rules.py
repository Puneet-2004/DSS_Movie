from datetime import datetime
from typing import List, Tuple

from app.conversation.schema import UserPreferences
from app.retrieval.models import MovieShowtimeCandidate


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _matches_any(source_values: List[str], preferred_values: List[str]) -> bool:
    source_normalized = {_normalize(v) for v in source_values if v is not None}
    preferred_normalized = [_normalize(v) for v in preferred_values if v is not None]
    return any(value in source_normalized for value in preferred_normalized)


def _parse_hour(showtime: str):
    try:
        dt = datetime.strptime(showtime.strip().upper(), "%I:%M %p")
        return dt.hour
    except ValueError:
        return None


def _matches_time_range(showtime: str, preferred_time_range: str) -> bool:
    hour = _parse_hour(showtime)
    if hour is None:
        return True

    preferred_time_range = _normalize(preferred_time_range)

    if preferred_time_range == "morning":
        return 5 <= hour < 12
    if preferred_time_range == "afternoon":
        return 12 <= hour < 17
    if preferred_time_range == "evening":
        return 17 <= hour < 20
    if preferred_time_range == "night":
        return 20 <= hour <= 23

    return True


def _title_matches(selected_title: str, movie_title: str) -> bool:
    selected = _normalize(selected_title)
    title = _normalize(movie_title)
    return selected in title or title in selected


def hard_filter_candidates(
    preferences: UserPreferences,
    candidates: List[MovieShowtimeCandidate],
) -> Tuple[List[MovieShowtimeCandidate], List[dict]]:
    kept = []
    rejected = []

    for candidate in candidates:
        reasons = []

        if preferences.selected_movie_title:
            if not _title_matches(preferences.selected_movie_title, candidate.movie_title):
                reasons.append("movie title does not match requested movie")

        if preferences.budget is not None and candidate.ticket_price is not None:
            if candidate.ticket_price > preferences.budget:
                reasons.append("ticket price exceeds budget")

        if preferences.max_travel_distance_km is not None and candidate.distance_km is not None:
            if candidate.distance_km > preferences.max_travel_distance_km:
                reasons.append("distance exceeds travel limit")

        if preferences.preferred_languages and candidate.language:
            if not _matches_any([candidate.language], preferences.preferred_languages):
                reasons.append("language does not match preference")

        if preferences.preferred_time_range and candidate.showtime:
            if not _matches_time_range(candidate.showtime, preferences.preferred_time_range):
                reasons.append("showtime does not match preferred time range")

        if reasons:
            rejected.append(
                {
                    "candidate": candidate,
                    "reasons": reasons,
                }
            )
        else:
            kept.append(candidate)

    return kept, rejected