# Nion Orchestration Engine - Decisions Agent
# L3 agent for extracting decisions

from typing import Type

from models.l3_models import DecisionsResult
from prompts import L3_DECISIONS_PROMPT
from .base import BaseL3Agent


class DecisionsAgent(BaseL3Agent[DecisionsResult]):
    """L3 agent for extracting decisions and resolutions"""
    
    name: str = "decisions_agent"
    description: str = "Extracts decisions, resolutions, and agreements"
    
    def __init__(self):
        super().__init__(system_prompt=L3_DECISIONS_PROMPT)
    
    @property
    def result_model(self) -> Type[DecisionsResult]:
        return DecisionsResult
    
    @property
    def empty_result(self) -> DecisionsResult:
        return DecisionsResult(items=[])


# Singleton instance
decisions_agent = DecisionsAgent()
