from abc import ABC, abstractmethod


class LLMClient(ABC):
    name: str

    @abstractmethod
    def complete_json(self, system: str, user: str, schema: dict) -> dict:
        """Return a dict that conforms to the JSON schema."""
