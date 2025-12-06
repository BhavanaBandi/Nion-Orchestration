# Nion Orchestration Engine - Enhanced L2 Coordinator
# Domain routing layer with support for all L3 agents

import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

from models.l1_models import L1Task, L1TaskPlan, DomainType, L3AgentType
from models.l3_models import ExtractionResult, ActionItemsResult, RisksResult, DecisionsResult

logger = logging.getLogger(__name__)


@dataclass
class L2RoutingResult:
    """Result of L2 routing and execution"""
    task: L1Task
    domain: str
    l3_agent: Optional[str]
    extraction_result: Optional[ExtractionResult]
    success: bool
    error: Optional[str] = None
    status: str = "COMPLETED"


class L2Coordinator:
    """
    L2 Coordinator - Routes tasks to appropriate L3 agents.
    
    Supports enhanced routing with:
    - All L3 agent types from testio.md
    - Task dependencies
    - Cross-cutting concerns
    """
    
    # Valid domains for routing validation
    VALID_DOMAINS: set = {
        "TRACKING_EXECUTION",
        "COMMUNICATION_COLLABORATION", 
        "LEARNING_IMPROVEMENT"
    }
    
    # L3 agent types for cross-cutting concerns
    L3_AGENTS: set = {
        "action_item_extraction",
        "risk_extraction",
        "decision_extraction",
        "knowledge_retrieval",
        "qna",
        "evaluation",
        "message_delivery"
    }
    
    def __init__(self):
        # Lazy initialization to avoid circular imports
        self._agent_map: Dict[str, Callable] = {}
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of agent map"""
        if not self._initialized:
            from orchestration.l3_agents import (
                action_items_agent,
                risks_agent,
                decisions_agent,
                knowledge_retrieval_agent,
                qna_agent,
                evaluation_agent,
                message_delivery_agent
            )
            
            # Map L3 agent types to agent instances
            self._agent_map = {
                "action_item_extraction": action_items_agent,
                "risk_extraction": risks_agent,
                "decision_extraction": decisions_agent,
                "knowledge_retrieval": knowledge_retrieval_agent,
                "qna": qna_agent,
                "evaluation": evaluation_agent,
                "message_delivery": message_delivery_agent,
            }
            
            # Default agents for domains (when l3_agent not specified)
            self._domain_defaults = {
                "TRACKING_EXECUTION": action_items_agent,
                "COMMUNICATION_COLLABORATION": qna_agent,
                "LEARNING_IMPROVEMENT": decisions_agent,
            }
            
            self._initialized = True
    
    def get_agent(self, task: L1Task) -> Optional[Callable]:
        """Get the agent for a task"""
        self._ensure_initialized()
        
        # If specific L3 agent is specified, use it
        if task.l3_agent and task.l3_agent in self._agent_map:
            return self._agent_map[task.l3_agent]
        
        # Fall back to domain default
        return self._domain_defaults.get(task.domain)
    
    async def route_task(
        self,
        task: L1Task,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> L2RoutingResult:
        """
        Route a single task to its L3 agent and execute.
        
        Args:
            task: The L1 task to route
            content: The original content for extraction
            context: Additional context (accumulated results)
            
        Returns:
            L2RoutingResult with extraction output
        """
        agent_type = task.l3_agent or "default"
        logger.info(f"L2 Coordinator: Routing task {task.task_id} to {task.domain}/{agent_type}")
        
        agent = self.get_agent(task)
        
        if agent is None:
            return L2RoutingResult(
                task=task,
                domain=task.domain,
                l3_agent=task.l3_agent,
                extraction_result=None,
                success=False,
                error=f"No agent found for task: {task.task_id}",
                status="FAILED"
            )
        
        try:
            # Build extraction content with context if available
            extraction_content = content
            if context:
                # Format context nicely for the agent
                context_parts = []
                for dep_id, dep_data in context.items():
                    # Extract key information from dependency results
                    if isinstance(dep_data, dict):
                        if 'response' in dep_data:
                            # QnA response - this is what evaluation needs
                            context_parts.append(f"Response to evaluate:\n{dep_data['response']}")
                        elif 'items' in dep_data:
                            # Extraction results
                            items = dep_data['items']
                            if items:
                                context_parts.append(f"Extracted from {dep_id}: {len(items)} items")
                        else:
                            context_parts.append(f"{dep_id}: {dep_data}")
                
                if context_parts:
                    extraction_content = f"{content}\n\n--- Previous Results ---\n" + "\n".join(context_parts)
            
            # Execute the agent
            result = await agent.extract(extraction_content, task.task_id)
            
            return L2RoutingResult(
                task=task,
                domain=task.domain,
                l3_agent=task.l3_agent or agent.name,
                extraction_result=result,
                success=True,
                status="COMPLETED"
            )
            
        except Exception as e:
            logger.error(f"L3 agent error for task {task.task_id}: {e}")
            return L2RoutingResult(
                task=task,
                domain=task.domain,
                l3_agent=task.l3_agent,
                extraction_result=None,
                success=False,
                error=str(e),
                status="FAILED"
            )
    
    async def route_all_tasks(
        self,
        task_plan: L1TaskPlan,
        content: str
    ) -> List[L2RoutingResult]:
        """
        Route all tasks in a plan to their L3 agents.
        Respects task dependencies using topological sort.
        
        Args:
            task_plan: The L1 task plan
            content: The original content for extraction
            
        Returns:
            List of routing results in execution order
        """
        logger.info(f"L2 Coordinator: Routing {len(task_plan.tasks)} tasks")
        
        # Get tasks in dependency order
        ordered_tasks = task_plan.get_execution_order()
        
        results = []
        completed_results: Dict[str, L2RoutingResult] = {}
        
        for task in ordered_tasks:
            # Build context from dependencies
            context = {}
            for dep_id in task.depends_on:
                if dep_id in completed_results and completed_results[dep_id].extraction_result:
                    context[dep_id] = completed_results[dep_id].extraction_result.model_dump(mode='json')
            
            # Route and execute
            result = await self.route_task(task, content, context if context else None)
            results.append(result)
            completed_results[task.task_id] = result
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"L2 Coordinator: {successful}/{len(results)} tasks completed successfully")
        
        return results


# Convenience function
async def route_and_execute(
    task_plan: L1TaskPlan,
    content: str
) -> List[L2RoutingResult]:
    """
    Route and execute all tasks in a plan.
    
    Args:
        task_plan: The task plan from L1
        content: Original content for extraction
        
    Returns:
        List of routing results
    """
    coordinator = L2Coordinator()
    return await coordinator.route_all_tasks(task_plan, content)
