# Nion Orchestration Engine - Risks Agent
# L3 agent for extracting risks and blockers

from typing import Type

from models.l3_models import RisksResult
from prompts import L3_RISKS_PROMPT
from .base import BaseL3Agent


class RisksAgent(BaseL3Agent[RisksResult]):
    """L3 agent for extracting risks, blockers, and concerns"""
    
    name: str = "risks_agent"
    description: str = "Extracts risks, blockers, and potential issues"
    
    def __init__(self):
        super().__init__(system_prompt=L3_RISKS_PROMPT)
    
    @property
    def result_model(self) -> Type[RisksResult]:
        return RisksResult
    
    @property
    def empty_result(self) -> RisksResult:
        return RisksResult(items=[])


# Singleton instance
risks_agent = RisksAgent()
