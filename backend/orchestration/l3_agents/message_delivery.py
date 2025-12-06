# Nion Orchestration Engine - Message Delivery Agent
# L3 agent for message delivery metadata

from typing import Type, Optional

from models.l3_models import MessageDeliveryResult
from prompts import L3_MESSAGE_DELIVERY_PROMPT, L3_EXTRACTION_USER_PROMPT
from .base import BaseL3Agent


class MessageDeliveryAgent(BaseL3Agent[MessageDeliveryResult]):
    """L3 agent for preparing message delivery"""
    
    name: str = "message_delivery_agent"
    description: str = "Prepares message delivery metadata"
    
    def __init__(self):
        super().__init__(system_prompt=L3_MESSAGE_DELIVERY_PROMPT)
    
    @property
    def result_model(self) -> Type[MessageDeliveryResult]:
        return MessageDeliveryResult
    
    @property
    def empty_result(self) -> MessageDeliveryResult:
        return MessageDeliveryResult(
            channel="email",
            recipient="Unknown",
            cc=[],
            delivery_status="PENDING"
        )
    
    async def extract_with_context(
        self,
        content: str,
        source_task_id: Optional[str] = None,
        channel: Optional[str] = None,
        recipient: Optional[str] = None
    ) -> MessageDeliveryResult:
        """
        Extract with additional context for delivery.
        
        Args:
            content: Content context
            source_task_id: Task ID
            channel: Original message channel
            recipient: Original sender (becomes recipient for reply)
            
        Returns:
            MessageDeliveryResult
        """
        result = await super().extract(content, source_task_id)
        if channel:
            result.channel = channel
        if recipient:
            result.recipient = recipient
        result.delivery_status = "SENT"  # MVP mode
        return result


# Singleton instance
message_delivery_agent = MessageDeliveryAgent()
