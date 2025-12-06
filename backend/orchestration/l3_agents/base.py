# Nion Orchestration Engine - L3 Agent Base
# Base class for extraction agents

import logging
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic, Type
from pydantic import BaseModel, ValidationError

from llm.grok_client import grok_client, GrokClient
from prompts import L3_EXTRACTION_USER_PROMPT

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class BaseL3Agent(ABC, Generic[T]):
    """
    Base class for L3 extraction agents.
    
    Inspired by OpenManus BaseAgent pattern:
    - Abstract base with common functionality
    - Pydantic model validation
    - Standardized extraction interface
    """
    
    name: str = "base_agent"
    description: str = "Base extraction agent"
    
    def __init__(
        self,
        client: Optional[GrokClient] = None,
        system_prompt: str = ""
    ):
        self.client = client or grok_client
        self.system_prompt = system_prompt
    
    @property
    @abstractmethod
    def result_model(self) -> Type[T]:
        """The Pydantic model for the extraction result"""
        pass
    
    @property
    @abstractmethod
    def empty_result(self) -> T:
        """Return an empty result instance"""
        pass
    
    def _build_user_prompt(self, content: str) -> str:
        """Build the user prompt with content"""
        return L3_EXTRACTION_USER_PROMPT.format(content=content)
    
    async def extract(
        self,
        content: str,
        source_task_id: Optional[str] = None
    ) -> T:
        """
        Extract information from content.
        
        Args:
            content: The content to extract from
            source_task_id: Optional task ID for tracking
            
        Returns:
            Extraction result of type T
        """
        if not content or not content.strip():
            logger.debug(f"{self.name}: Empty content, returning empty result")
            return self.empty_result
        
        logger.info(f"{self.name}: Extracting from content ({len(content)} chars)")
        
        try:
            user_prompt = self._build_user_prompt(content)
            
            raw_response = await self.client.complete(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )
            
            return self._parse_response(raw_response, source_task_id)
            
        except Exception as e:
            logger.error(f"{self.name} extraction error: {e}")
            return self.empty_result
    
    def _parse_response(
        self,
        raw_response: str,
        source_task_id: Optional[str] = None
    ) -> T:
        """Parse the LLM response into a result model"""
        try:
            data = GrokClient.extract_json(raw_response)
            
            # Add source_task_id if present
            if source_task_id and "source_task_id" not in data:
                data["source_task_id"] = source_task_id
            
            return self.result_model.model_validate(data)
            
        except (ValueError, ValidationError) as e:
            logger.warning(f"{self.name}: Failed to parse response: {e}")
            return self.empty_result
