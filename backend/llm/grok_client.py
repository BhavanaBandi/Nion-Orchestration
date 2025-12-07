# Nion Orchestration Engine - LLM Client
# Wrapper for Gemini API (gemini-2.5-flash), Groq (LLaMA 3), and OpenAI with retry logic and JSON extraction

import re
import json
import logging
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import config

logger = logging.getLogger(__name__)

# Gemini SDK import (conditional to avoid errors if not installed)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed, Gemini provider unavailable")


class LLMClientError(Exception):
    """Base exception for LLM client errors"""
    pass


class LLMAPIError(LLMClientError):
    """Error from LLM API"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"LLM API error ({status_code}): {message}")


class LLMClient:
    """
    Wrapper for LLM API calls with retry logic.
    Supports Gemini (gemini-2.5-flash), Groq (LLaMA 3), and OpenAI (GPT-4o).
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
        self.provider = config.llm.provider
        
        # Initialize Gemini client if using gemini provider
        self.gemini_client = None
        if self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise LLMClientError("Gemini provider requested but google-generativeai is not installed")
            if not self.api_key:
                logger.warning("GEMINI_API_KEY not set - LLM calls will fail")
            else:
                try:
                    genai.configure(api_key=self.api_key)
                    self.gemini_model = genai.GenerativeModel(self.model)
                    logger.info(f"Gemini initialized with model: {self.model}")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini: {e}")

    async def _complete_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Complete using Gemini SDK (google-generativeai)"""
        try:
            # Gemini models often take system prompt in initialization, but for chat we can prepend it
            # or use the system_instruction if model supports it (Gemini 1.5 Pro does).
            # Re-initializing model with proper system instruction for each call is safer for statelessness
            # or we just prepend to user prompt if we want to be simple.
            # Let's use the explicit system_instruction if available in this SDK version,
            # else prepend.
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Create a fresh model instance to pass system_instruction (supported in newer versions)
            # or just use the cached one if we don't care about system instruction safety.
            # Safe bet: Prepend system prompt to user prompt for max compatibility or use system_instruction arg
            
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt
            )
            
            # Run in executor because generate_content is synchronous
            import asyncio
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    user_prompt,
                    generation_config=generation_config
                )
            )
            
            content = response.text
            logger.debug(f"Gemini response: {content[:200]}...")
            return content
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            # Fallback for Rate Limits
            if "429" in str(e) or "quota" in str(e).lower() or "resource_exhausted" in str(e).lower():
                logger.warning("Rate limit hit! Using MOCK/DEMO response for reliability.")
                from .mock_data import get_mock_response
                return get_mock_response(user_prompt)
            raise
    
    async def _complete_openai_compatible(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Complete using OpenAI-compatible API (Groq, OpenAI)"""
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
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"LLM API error: {response.status_code} - {error_text}")
                    
                    # Mock Mode / Demo Fallback for 429 logic
                    if response.status_code == 429:
                        logger.warning("Rate limit hit! Using MOCK/DEMO response for reliability.")
                        from .mock_data import get_mock_response
                        return get_mock_response(user_prompt)
                    
                    raise LLMAPIError(response.status_code, error_text)
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                logger.debug(f"LLM response: {content[:200]}...")
                return content
                
        except Exception as e:
            logger.error(f"LLM Call Failed: {e}")
            raise

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
        
        # Last Resort: If we are in demo mode and failed to parse, maybe return specific mock?
        # But complete() handles the HTTP errors. If we got here, we got '200 OK' but bad JSON.
        
        raise ValueError(f"Could not extract JSON from response: {raw[:200]}...")


# Singleton instance for convenience
llm_client = LLMClient()

# Backwards compatibility alias
grok_client = llm_client
GroqClient = LLMClient
GrokClient = LLMClient
