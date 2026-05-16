import json
from json import JSONDecodeError

from app.conversation.schema import UserPreferences
from app.llm.ollama_client import OllamaClient


class PreferenceExtractor:
    def __init__(self):
        self.client = OllamaClient()

        with open("prompts/extraction_prompt.txt", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

    def extract(self, user_message: str) -> UserPreferences:
        full_prompt = f"""
{self.system_prompt}

User Input:
{user_message}
"""

        response = self.client.generate(full_prompt)
        cleaned_response = response.strip()

        print("\n========== RAW MODEL RESPONSE ==========")
        print(cleaned_response)
        print("========================================\n")

        start_index = cleaned_response.find("{")
        end_index = cleaned_response.rfind("}")

        if start_index == -1 or end_index == -1 or end_index <= start_index:
            raise ValueError("Model did not return a JSON object.")

        json_string = cleaned_response[start_index:end_index + 1]

        try:
            data = json.loads(json_string)
        except JSONDecodeError as exc:
            raise ValueError(
                f"Could not parse model output as JSON: {json_string}"
            ) from exc

        return UserPreferences(**data)