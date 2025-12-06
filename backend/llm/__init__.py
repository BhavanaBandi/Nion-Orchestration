# LLM package
from .grok_client import (
    GroqClient, 
    llm_client, 
    LLMClientError, 
    LLMAPIError,
    # Backwards compatibility aliases
    GrokClient,
    grok_client
)

__all__ = [
    "GroqClient", 
    "llm_client", 
    "LLMClientError", 
    "LLMAPIError",
    # Backwards compatibility
    "GrokClient",
    "grok_client",
]
