# Nion Orchestration Engine - Enhanced L1 Orchestrator
# Strategic task planning layer with message metadata

import json
import logging
from typing import Optional, Dict, Any
from pydantic import ValidationError

from models.l1_models import L1Task, L1TaskPlan, L1OrchestratorResult, Message, Sender
from llm.grok_client import llm_client, GroqClient
from prompts import L1_SYSTEM_PROMPT, L1_USER_PROMPT

logger = logging.getLogger(__name__)


class L1Orchestrator:
    """
    L1 Strategic Orchestrator - Plans tasks from messages.
    
    Supports enhanced message format from testio.md with:
    - Sender info (name, role)
    - Source (email, slack, meeting)
    - Project context
    - Task dependencies
    """
    
    def __init__(
        self,
        client: Optional[GroqClient] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.client = client or llm_client
        self.context = context or {}
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with context injection"""
        context_str = json.dumps(self.context, indent=2) if self.context else "{}"
        return L1_SYSTEM_PROMPT.format(context=context_str)
    
    def _build_user_prompt(self, message: Message) -> str:
        """Build user prompt with full message metadata"""
        return L1_USER_PROMPT.format(
            message_id=message.message_id,
            source=message.source,
            sender_name=message.sender.name,
            sender_role=message.sender.role or "Unknown",
            project=message.project or "Not specified",
            content=message.content
        )
    
    async def plan_tasks(
        self,
        message: Message
    ) -> L1OrchestratorResult:
        """
        Generate a task plan from the input message.
        
        Args:
            message: The Message object with full metadata
            
        Returns:
            L1OrchestratorResult containing the task plan
        """
        logger.info(f"L1 Orchestrator: Planning tasks for message {message.message_id}")

        # [NEW] Timeline Analysis
        try:
            from orchestration.timeline_engine import TimelineEngine
            timeline_engine = TimelineEngine(client=self.client)
            timeline_result = await timeline_engine.analyze(message.content)
            
            # Format timeline context for L1 Prompt
            timeline_context = json.dumps(timeline_result.model_dump(mode='json'), indent=2)
            logger.info(f"L1 Timeline Analysis: {len(timeline_result.events)} events found")
            
            # If conflicts/recommendations exist, inject them
            if timeline_result.conflicts or timeline_result.recommendations:
                logger.warning(f"L1 Timeline Conflicts: {len(timeline_result.conflicts)}")
        except Exception as e:
            logger.error(f"L1 Timeline Engine failed: {e}")
            timeline_context = "Timeline analysis failed."

        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(message)
        
        # Inject timeline insights into prompt
        user_prompt += f"\n\n## Timeline Analysis (Auto-Generated)\n{timeline_context}\n\nUse this timeline data to generate task deadlines and identify clarification needs."
        
        try:
            # Call Groq LLM
            raw_response = await self.client.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3  # Low temperature for consistent output
            )
            
            logger.debug(f"L1 raw response: {raw_response[:500]}")
            
            # Parse response
            task_plan = self._parse_response(raw_response, message)
            
            return L1OrchestratorResult(
                success=True,
                task_plan=task_plan,
                raw_response=raw_response
            )
            
        except Exception as e:
            logger.error(f"L1 Orchestrator error: {e}")
            return L1OrchestratorResult(
                success=False,
                task_plan=L1TaskPlan(
                    source_message_id=message.message_id,
                    source_message=message
                ),
                error=str(e)
            )
    
    async def plan_tasks_from_dict(
        self,
        message_dict: Dict[str, Any]
    ) -> L1OrchestratorResult:
        """
        Generate a task plan from a message dictionary.
        Convenience method for testio.md format.
        
        Args:
            message_dict: Dictionary matching Message schema
            
        Returns:
            L1OrchestratorResult containing the task plan
        """
        # Parse sender
        sender_data = message_dict.get("sender", {})
        if isinstance(sender_data, dict):
            sender = Sender(
                name=sender_data.get("name", "Unknown"),
                role=sender_data.get("role")
            )
        else:
            sender = Sender(name="Unknown")
        
        # Create Message object
        message = Message(
            message_id=message_dict.get("message_id", message_dict.get("id", "MSG-UNKNOWN")),
            source=message_dict.get("source", "email"),
            sender=sender,
            content=message_dict.get("content", message_dict.get("body", "")),
            project=message_dict.get("project")
        )
        
        return await self.plan_tasks(message)
    
    def _parse_response(
        self,
        raw_response: str,
        message: Message
    ) -> L1TaskPlan:
        """
        Parse LLM response into L1TaskPlan with fallback strategies.
        """
        try:
            # Extract JSON from response
            data = GroqClient.extract_json(raw_response)
            
            # Validate with Pydantic
            tasks = []
            for task_data in data.get("tasks", []):
                try:
                    task = L1Task.model_validate(task_data)
                    tasks.append(task)
                except ValidationError as e:
                    logger.warning(f"Invalid task data: {task_data}, error: {e}")
                    continue
            
            return L1TaskPlan(
                tasks=tasks,
                source_message_id=message.message_id,
                source_message=message
            )
            
        except ValueError as e:
            logger.warning(f"Failed to extract JSON: {e}, returning empty plan")
            return L1TaskPlan(
                source_message_id=message.message_id,
                source_message=message
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing L1 response: {e}")
            return L1TaskPlan(
                source_message_id=message.message_id,
                source_message=message
            )
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Update the context for future planning calls"""
        self.context = context
        logger.debug(f"L1 Orchestrator context updated: {list(context.keys())}")


# Convenience function for simple usage
async def plan_tasks(
    message_dict: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> L1OrchestratorResult:
    """
    Convenience function to plan tasks from a message dictionary.
    
    Args:
        message_dict: Message data matching testio.md format
        context: Optional context dictionary
        
    Returns:
        L1OrchestratorResult
    """
    orchestrator = L1Orchestrator(context=context)
    return await orchestrator.plan_tasks_from_dict(message_dict)
