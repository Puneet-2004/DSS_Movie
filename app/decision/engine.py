from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from app.conversation.schema import UserPreferences
from app.decision.rules import hard_filter_candidates
from app.decision.scoring import score_candidate
from app.retrieval.models import MovieShowtimeCandidate, RetrievalResult


@dataclass
class RankedCandidate:
    candidate: MovieShowtimeCandidate
    total_score: float
    score_breakdown: Dict[str, float]
    reasons: List[str]


@dataclass
class DecisionResult:
    ranked_candidates: List[RankedCandidate]
    recommended_candidate: Optional[RankedCandidate]
    rejected_candidates: List[dict]
    summary: List[str]


class DecisionEngine:
    def evaluate(
        self,
        preferences: UserPreferences,
        retrieval_result: RetrievalResult,
    ) -> DecisionResult:
        kept, rejected = hard_filter_candidates(
            preferences,
            retrieval_result.candidates,
        )

        ranked: List[RankedCandidate] = []

        for candidate in kept:
            total_score, breakdown = score_candidate(preferences, candidate)

            reasons = self._build_reasons(preferences, candidate, breakdown)

            candidate.score = total_score
            candidate.score_breakdown = breakdown
            candidate.decision_reasons = reasons

            ranked.append(
                RankedCandidate(
                    candidate=candidate,
                    total_score=total_score,
                    score_breakdown=breakdown,
                    reasons=reasons,
                )
            )

        ranked.sort(key=lambda item: item.total_score, reverse=True)

        recommended = ranked[0] if ranked else None

        summary = [
            f"Kept {len(kept)} candidate(s) after hard filters.",
            f"Rejected {len(rejected)} candidate(s) due to hard constraints.",
        ]

        if recommended:
            summary.append(
                f"Top candidate: {recommended.candidate.movie_title} at {recommended.candidate.theater_name}"
            )

        return DecisionResult(
            ranked_candidates=ranked,
            recommended_candidate=recommended,
            rejected_candidates=rejected,
            summary=summary,
        )

    def _build_reasons(
        self,
        preferences: UserPreferences,
        candidate: MovieShowtimeCandidate,
        breakdown: Dict[str, float],
    ) -> List[str]:
        reasons: List[str] = []

        if preferences.selected_movie_title and breakdown.get("title", 0) >= 1.0:
            reasons.append("matches the requested movie title")

        if breakdown.get("genre", 0) >= 0.5 and preferences.preferred_genres:
            reasons.append("fits the preferred genre")

        if breakdown.get("budget", 0) >= 0.7 and preferences.budget is not None:
            reasons.append("fits the budget")

        if breakdown.get("travel", 0) >= 0.7 and preferences.max_travel_distance_km is not None:
            reasons.append("is within the travel limit")

        if breakdown.get("time", 0) >= 0.5 and preferences.preferred_time_range:
            reasons.append("fits the preferred time window")

        if breakdown.get("food", 0) >= 0.7 and preferences.wants_food:
            reasons.append("has food or refreshment support")

        if breakdown.get("rating", 0) >= 0.6:
            reasons.append("has a reasonable rating")

        return reasons