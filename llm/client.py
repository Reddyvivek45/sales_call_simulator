from config import LLM_PROVIDER

from llm.ollama_client import OllamaClient
from llm.groq_client import GroqClient


def get_llm_client():

    if LLM_PROVIDER == "ollama":
        return OllamaClient()

    if LLM_PROVIDER == "groq":
        return GroqClient()

    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )