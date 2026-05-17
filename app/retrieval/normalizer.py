from typing import Any, Dict

from app.retrieval.models import MovieShowtimeCandidate


def normalize_candidate(raw: Dict[str, Any]) -> MovieShowtimeCandidate:
    return MovieShowtimeCandidate(
        movie_title=str(raw.get("movie_title", "")).strip(),
        theater_name=str(raw.get("theater_name", "")).strip(),
        showtime=str(raw.get("showtime", "")).strip(),
        ticket_price=raw.get("ticket_price"),
        location=raw.get("location"),
        distance_km=raw.get("distance_km"),
        language=raw.get("language"),
        genres=list(raw.get("genres") or []),
        amenities=list(raw.get("amenities") or []),
        source_name=str(raw.get("source_name", "")).strip(),
        source_url=str(raw.get("source_url", "")).strip(),
        raw=raw,
    )