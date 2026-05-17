from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RetrievalQuery:
    location: str
    preferred_date: str
    budget: Optional[int] = None
    max_travel_distance_km: Optional[int] = None

    preferred_genres: List[str] = field(default_factory=list)
    preferred_languages: List[str] = field(default_factory=list)

    preferred_time_range: Optional[str] = None

    wants_food: Optional[bool] = None

    preferred_formats: List[str] = field(default_factory=list)

    selected_movie_title: Optional[str] = None


@dataclass
class MovieShowtimeCandidate:
    movie_title: str

    theater_name: str

    showtime: str

    ticket_price: Optional[int] = None

    location: Optional[str] = None

    distance_km: Optional[float] = None

    language: Optional[str] = None

    genres: List[str] = field(default_factory=list)

    amenities: List[str] = field(default_factory=list)

    source_name: str = ""

    source_url: str = ""

    retrieval_strategy: str = ""

    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalMetadata:
    retrieval_strategy: str

    candidate_count: int

    selected_movie_title: Optional[str] = None


@dataclass
class RetrievalResult:
    query: RetrievalQuery

    metadata: RetrievalMetadata

    candidates: List[MovieShowtimeCandidate] = field(default_factory=list)

    source_notes: List[str] = field(default_factory=list)