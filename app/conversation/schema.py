from typing import List, Optional

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    location: Optional[str] = None
    budget: Optional[int] = None

    preferred_genres: Optional[List[str]] = Field(default_factory=list)
    preferred_languages: Optional[List[str]] = Field(default_factory=list)

    companions: Optional[str] = None
    max_travel_distance_km: Optional[int] = None

    preferred_date: Optional[str] = None
    preferred_time_range: Optional[str] = None

    wants_food: Optional[bool] = None
    preferred_formats: Optional[List[str]] = Field(default_factory=list)

    flexibility_level: Optional[str] = None
    selected_movie_title: Optional[str] = None

    def merge_with(self, other: "UserPreferences") -> "UserPreferences":
        current = self.model_dump()
        incoming = other.model_dump()
        merged = {}

        for key, current_value in current.items():
            new_value = incoming.get(key)

            if isinstance(current_value, list):
                if not new_value:
                    merged[key] = current_value
                else:
                    merged[key] = list(dict.fromkeys((current_value or []) + new_value))
            else:
                if new_value is None:
                    merged[key] = current_value
                elif isinstance(new_value, str) and not new_value.strip():
                    merged[key] = current_value
                else:
                    merged[key] = new_value

        return UserPreferences(**merged)