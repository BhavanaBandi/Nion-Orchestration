# Nion Orchestration Engine - Groq LLM Client
# Wrapper for Groq API (LLaMA 3 70B) with retry logic and JSON extraction

import re
import json
import logging
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import config

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Base exception for LLM client errors"""
    pass


class LLMAPIError(LLMClientError):
    """Error from LLM API"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"LLM API error ({status_code}): {message}")


class GroqClient:
    """
    Wrapper for Groq API calls with retry logic.
    Uses LLaMA 3 70B model (GPT OSS equivalent).
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        self.api_key = api_key or config.llm.api_key
        self.base_url = base_url or config.llm.base_url
        self.model = model or config.llm.model
        self.timeout = timeout or config.llm.timeout
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set - API calls will fail")
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        Call Groq API with retry logic.
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User message content
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response tokens
            
        Returns:
            Raw text response from LLM
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        logger.info(f"Calling Groq API with model: {self.model}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Groq API error: {response.status_code} - {error_text}")
                raise LLMAPIError(response.status_code, error_text)
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.debug(f"Groq response: {content[:200]}...")
            return content
    
    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3  # Lower temp for structured output
    ) -> Dict[str, Any]:
        """
        Get response and parse as JSON with fallback extraction.
        
        Args:
            system_prompt: System-level instructions (should include JSON formatting)
            user_prompt: User message content
            temperature: Lower temperature for more deterministic output
            
        Returns:
            Parsed JSON as dictionary
        """
        raw = await self.complete(system_prompt, user_prompt, temperature)
        return self.extract_json(raw)
    
    @staticmethod
    def extract_json(raw: str) -> Dict[str, Any]:
        """
        Extract JSON from response with multiple fallback strategies.
        
        Handles:
        - Direct JSON response
        - JSON wrapped in markdown code blocks
        - JSON embedded in other text
        """
        stripped = raw.strip()
        
        # Strategy 1: Direct parse
        if stripped.startswith('{') or stripped.startswith('['):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass
        
        # Strategy 2: Extract from markdown code block
        pattern = r'```(?:json)?\s*([\s\S]*?)```'
        match = re.search(pattern, raw)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Find first { to last }
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end+1])
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Find first [ to last ]
        start = raw.find('[')
        end = raw.rfind(']')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end+1])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Could not extract JSON from response: {raw[:200]}...")


# Singleton instance for convenience
llm_client = GroqClient()

# Backwards compatibility alias
grok_client = llm_client
GrokClient = GroqClient
