# Nion Orchestration Engine - Q&A Agent
# L3 agent for formulating gap-aware responses

from typing import Type

from models.l3_models import QnAResponse
from prompts import L3_QNA_PROMPT, L3_EXTRACTION_USER_PROMPT
from .base import BaseL3Agent


class QnAAgent(BaseL3Agent[QnAResponse]):
    """L3 agent for formulating gap-aware responses"""
    
    name: str = "qna_agent"
    description: str = "Formulates responses acknowledging knowledge gaps"
    
    def __init__(self):
        super().__init__(system_prompt=L3_QNA_PROMPT)
    
    @property
    def result_model(self) -> Type[QnAResponse]:
        return QnAResponse
    
    @property
    def empty_result(self) -> QnAResponse:
        return QnAResponse(
            response="Unable to formulate response due to insufficient context.",
            what_i_know=[],
            what_i_logged=[],
            what_i_need=["More context required"]
        )


# Singleton instance
qna_agent = QnAAgent()
