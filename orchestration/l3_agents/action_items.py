# Nion Orchestration Engine - Action Items Agent
# L3 agent for extracting action items

from typing import Type

from models.l3_models import ActionItemsResult
from prompts import L3_ACTION_ITEMS_PROMPT
from .base import BaseL3Agent


class ActionItemsAgent(BaseL3Agent[ActionItemsResult]):
    """L3 agent for extracting action items from content"""
    
    name: str = "action_items_agent"
    description: str = "Extracts action items, tasks, and to-dos"
    
    def __init__(self):
        super().__init__(system_prompt=L3_ACTION_ITEMS_PROMPT)
    
    @property
    def result_model(self) -> Type[ActionItemsResult]:
        return ActionItemsResult
    
    @property
    def empty_result(self) -> ActionItemsResult:
        return ActionItemsResult(items=[])


# Singleton instance
action_items_agent = ActionItemsAgent()
