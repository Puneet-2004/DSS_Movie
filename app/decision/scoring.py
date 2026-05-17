from typing import Dict, Tuple

from app.conversation.schema import UserPreferences
from app.retrieval.models import MovieShowtimeCandidate


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _title_score(preferences: UserPreferences, candidate: MovieShowtimeCandidate) -> float:
    if not preferences.selected_movie_title:
        return 0.0

    requested = _normalize(preferences.selected_movie_title)
    title = _normalize(candidate.movie_title)

    if requested in title or title in requested:
        return 1.0

    return 0.0


def _genre_score(preferences: UserPreferences, candidate: MovieShowtimeCandidate) -> float:
    if not preferences.preferred_genres:
        return 0.5

    if not candidate.genres:
        return 0.5

    pref = {_normalize(g) for g in preferences.preferred_genres}
    cand = {_normalize(g) for g in candidate.genres}

    overlap = pref.intersection(cand)
    return min(1.0, len(overlap) / max(1, len(pref)))


def _language_score(preferences: UserPreferences, candidate: MovieShowtimeCandidate) -> float:
    if not preferences.preferred_languages:
        return 0.5

    if not candidate.language:
        return 0.5

    pref = {_normalize(x) for x in preferences.preferred_languages}
    return 1.0 if _normalize(candidate.language) in pref else 0.0


def _budget_score(preferences: UserPreferences, candidate: MovieShowtimeCandidate) -> float:
    if preferences.budget is None:
        return 0.5

    if candidate.ticket_price is None:
        return 0.5

    if candidate.ticket_price > preferences.budget:
        return 0.0

    ratio = candidate.ticket_price / max(1, preferences.budget)
    return max(0.0, min(1.0, 1.0 - (ratio * 0.6)))


def _travel_score(preferences: UserPreferences, candidate: MovieShowtimeCandidate) -> float:
    if preferences.max_travel_distance_km is None:
        return 0.5

    if candidate.distance_km is None:
        return 0.5

    if candidate.distance_km > preferences.max_travel_distance_km:
        return 0.0

    ratio = candidate.distance_km / max(1.0, float(preferences.max_travel_distance_km))
    return max(0.0, min(1.0, 1.0 - (ratio * 0.7)))


def _time_score(preferences: UserPreferences, candidate: MovieShowtimeCandidate) -> float:
    if not preferences.preferred_time_range:
        return 0.5

    return 1.0 if candidate.showtime else 0.5


def _food_score(preferences: UserPreferences, candidate: MovieShowtimeCandidate) -> float:
    if preferences.wants_food is None:
        return 0.5

    has_food = any("food" in amenity.lower() for amenity in candidate.amenities)

    if preferences.wants_food:
        return 1.0 if has_food else 0.0

    return 0.5 if has_food else 1.0


def _rating_score(candidate: MovieShowtimeCandidate) -> float:
    rating = candidate.raw.get("rating")
    if rating is None:
        rating = candidate.raw.get("vote_average")

    if rating is None:
        return 0.5

    try:
        return max(0.0, min(1.0, float(rating) / 10.0))
    except (TypeError, ValueError):
        return 0.5


def _popularity_score(candidate: MovieShowtimeCandidate) -> float:
    popularity = candidate.raw.get("popularity")
    if popularity is None:
        return 0.5

    try:
        return max(0.0, min(1.0, float(popularity) / 20.0))
    except (TypeError, ValueError):
        return 0.5


def score_candidate(
    preferences: UserPreferences,
    candidate: MovieShowtimeCandidate,
) -> Tuple[float, Dict[str, float]]:
    breakdown = {
        "title": _title_score(preferences, candidate),
        "genre": _genre_score(preferences, candidate),
        "language": _language_score(preferences, candidate),
        "budget": _budget_score(preferences, candidate),
        "travel": _travel_score(preferences, candidate),
        "time": _time_score(preferences, candidate),
        "food": _food_score(preferences, candidate),
        "rating": _rating_score(candidate),
        "popularity": _popularity_score(candidate),
    }

    weights = {
        "title": 0.35 if preferences.selected_movie_title else 0.0,
        "genre": 0.20 if preferences.preferred_genres else 0.12,
        "language": 0.10 if preferences.preferred_languages else 0.0,
        "budget": 0.18 if preferences.budget is not None else 0.0,
        "travel": 0.12 if preferences.max_travel_distance_km is not None else 0.0,
        "time": 0.08 if preferences.preferred_time_range else 0.0,
        "food": 0.05 if preferences.wants_food is not None else 0.0,
        "rating": 0.04,
        "popularity": 0.03,
    }

    weighted_sum = 0.0
    total_weight = 0.0

    for key, score in breakdown.items():
        weight = weights.get(key, 0.0)
        weighted_sum += score * weight
        total_weight += weight

    if total_weight == 0:
        total_score = 0.0
    else:
        total_score = weighted_sum / total_weight

    return total_score, breakdown