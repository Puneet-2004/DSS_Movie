from dataclasses import dataclass, field

from app.conversation.schema import UserPreferences


@dataclass
class ConversationState:
    preferences: UserPreferences = field(default_factory=UserPreferences)
    history: list[dict] = field(default_factory=list)