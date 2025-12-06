# Nion Orchestration Engine - Knowledge Retrieval Agent
# L3 agent for retrieving project context

from typing import Type, Optional

from models.l3_models import KnowledgeResult
from prompts import L3_KNOWLEDGE_PROMPT, L3_EXTRACTION_USER_PROMPT
from .base import BaseL3Agent


class KnowledgeRetrievalAgent(BaseL3Agent[KnowledgeResult]):
    """L3 agent for retrieving project knowledge and context"""
    
    name: str = "knowledge_retrieval_agent"
    description: str = "Retrieves project context and timeline information"
    
    def __init__(self):
        super().__init__(system_prompt=L3_KNOWLEDGE_PROMPT)
    
    @property
    def result_model(self) -> Type[KnowledgeResult]:
        return KnowledgeResult
    
    @property
    def empty_result(self) -> KnowledgeResult:
        return KnowledgeResult(items={})
    
    async def extract(
        self,
        content: str,
        source_task_id: Optional[str] = None,
        project: Optional[str] = None
    ) -> KnowledgeResult:
        """
        Retrieve project knowledge.
        
        Args:
            content: Context to extract from
            source_task_id: Optional task ID
            project: Optional project ID
            
        Returns:
            KnowledgeResult with project information
        """
        result = await super().extract(content, source_task_id)
        if project and not result.project:
            result.project = project
        return result


# Singleton instance
knowledge_retrieval_agent = KnowledgeRetrievalAgent()
