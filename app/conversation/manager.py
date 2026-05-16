from app.conversation.schema import UserPreferences

REQUIRED_FIELDS = [
    "location",
    "budget",
    "preferred_date",
    "preferred_time_range",
]

QUESTION_MAP = {
    "location": "Which city or area should I search in?",
    "budget": "What is your budget for tickets?",
    "preferred_date": "Which date do you want to watch the movie?",
    "preferred_time_range": "What time of day do you want to go?",
}


class ConversationManager:
    def merge_preferences(
        self,
        current_preferences: UserPreferences,
        new_preferences: UserPreferences,
    ) -> UserPreferences:
        return current_preferences.merge_with(new_preferences)

    def get_missing_required_fields(self, preferences: UserPreferences):
        missing = []

        for field in REQUIRED_FIELDS:
            value = getattr(preferences, field)

            if value is None:
                missing.append(field)
            elif isinstance(value, list) and len(value) == 0:
                missing.append(field)
            elif isinstance(value, str) and not value.strip():
                missing.append(field)

        return missing

    def get_next_question(self, preferences: UserPreferences):
        missing_fields = self.get_missing_required_fields(preferences)

        if not missing_fields:
            return None

        return QUESTION_MAP.get(missing_fields[0])