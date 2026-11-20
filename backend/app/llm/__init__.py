from app import config
from app.llm.base import LLMClient


def get_llm() -> LLMClient:
    """LLM_PROVIDER=stub|claude|ollama (default stub, so nothing costs money by accident)."""
    provider = config.get("LLM_PROVIDER", "stub")
    if provider == "stub":
        from app.llm.stub import StubLLM
        return StubLLM()
    raise NotImplementedError(f"LLM_PROVIDER={provider!r} is not built yet")
