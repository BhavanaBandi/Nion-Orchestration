# Nion Orchestration Engine - Enhanced Map Renderer
# Renders orchestration results in testio.md format

from datetime import datetime
from typing import List, Optional, Dict, Any

from models.l1_models import L1TaskPlan, Message
from models.l3_models import (
    ActionItemsResult, RisksResult, DecisionsResult,
    KnowledgeResult, QnAResponse, EvaluationResult, MessageDeliveryResult
)
from orchestration.l2_coordinator import L2RoutingResult


class OrchestrationMapRenderer:
    """
    Renders orchestration results into testio.md format.
    """
    
    def __init__(self, message: Optional[Message] = None):
        self.message = message
        self.lines: List[str] = []
    
    def _add_header(self):
        """Add map header with message metadata"""
        self.lines.append("=" * 74)
        self.lines.append("NION ORCHESTRATION MAP")
        self.lines.append("=" * 74)
        
        if self.message:
            self.lines.append(f"Message: {self.message.message_id}")
            self.lines.append(f"From: {self.message.sender.name} ({self.message.sender.role or 'Unknown'})")
            if self.message.project:
                self.lines.append(f"Project: {self.message.project}")
        
        self.lines.append("")
    
    def _add_section(self, title: str):
        """Add a section header"""
        self.lines.append("=" * 74)
        self.lines.append(title)
        self.lines.append("=" * 74)
    
    def _add_task_plan(self, task_plan: L1TaskPlan):
        """Render the L1 task plan"""
        self._add_section("L1 PLAN")
        
        if not task_plan.tasks:
            self.lines.append("No tasks identified.")
            self.lines.append("")
            return
        
        for task in task_plan.tasks:
            # Format: [TASK-001] → L2:DOMAIN or L3:agent
            if task.l3_agent:
                target = f"L3:{task.l3_agent} (Cross-Cutting)"
            else:
                target = f"L2:{task.domain}"
            
            self.lines.append(f"[{task.task_id}] → {target}")
            self.lines.append(f"Purpose: {task.purpose or task.description}")
            
            if task.depends_on:
                self.lines.append(f"Depends On: {', '.join(task.depends_on)}")
            
            self.lines.append("")
    
    def _add_execution_results(self, routing_results: List[L2RoutingResult]):
        """Render L2/L3 execution results"""
        self._add_section("L2/L3 EXECUTION")
        
        for result in routing_results:
            task = result.task
            agent_name = result.l3_agent or "unknown"
            
            # Header for the task
            if task.l3_agent:
                self.lines.append(f"[{task.task_id}] L3:{task.l3_agent} (Cross-Cutting)")
            else:
                self.lines.append(f"[{task.task_id}] L2:{task.domain}")
                self.lines.append(f"└─▶ [{task.task_id}-A] L3:{agent_name}")
            
            self.lines.append(f"Status: {result.status}")
            
            if not result.success:
                self.lines.append(f"Error: {result.error}")
                self.lines.append("")
                continue
            
            self.lines.append("Output:")
            self._render_extraction_result(result.extraction_result)
            self.lines.append("")
    
    def _render_extraction_result(self, result):
        """Render extraction result based on type"""
        if result is None:
            self.lines.append("• No output")
            return
        
        if isinstance(result, ActionItemsResult):
            for item in result.items:
                item_id = item.id or "AI-XXX"
                self.lines.append(f'• {item_id}: "{item.action}"')
                flags_str = f"[{', '.join(item.flags)}]" if item.flags else ""
                self.lines.append(f"  Owner: {item.owner or '?'} | Due: {item.deadline or '?'} {flags_str}")
        
        elif isinstance(result, RisksResult):
            for risk in result.items:
                risk_id = risk.id or "RISK-XXX"
                self.lines.append(f'• {risk_id}: "{risk.description}"')
                self.lines.append(f"  Likelihood: {risk.likelihood} | Impact: {risk.impact}")
        
        elif isinstance(result, DecisionsResult):
            for dec in result.items:
                dec_id = dec.id or "DEC-XXX"
                self.lines.append(f'• {dec_id}: "{dec.decision}"')
                self.lines.append(f"  Decision Maker: {dec.decision_maker or '?'} | Status: {dec.status}")
        
        elif isinstance(result, KnowledgeResult):
            if result.project:
                self.lines.append(f"• Project: {result.project}")
            for key, value in result.items.items():
                display_key = key.replace("_", " ").title()
                self.lines.append(f"• {display_key}: {value}")
        
        elif isinstance(result, QnAResponse):
            self.lines.append(f'• Response: "{result.response[:200]}..."' if len(result.response) > 200 else f'• Response: "{result.response}"')
            if result.what_i_know:
                self.lines.append("")
                self.lines.append("WHAT I KNOW:")
                for item in result.what_i_know:
                    self.lines.append(f"• {item}")
            if result.what_i_logged:
                self.lines.append("")
                self.lines.append("WHAT I'VE LOGGED:")
                for item in result.what_i_logged:
                    self.lines.append(f"• {item}")
            if result.what_i_need:
                self.lines.append("")
                self.lines.append("WHAT I NEED:")
                for item in result.what_i_need:
                    self.lines.append(f"• {item}")
        
        elif isinstance(result, EvaluationResult):
            self.lines.append(f"• Relevance: {result.relevance}")
            self.lines.append(f"• Accuracy: {result.accuracy}")
            self.lines.append(f"• Tone: {result.tone}")
            self.lines.append(f"• Gaps Acknowledged: {result.gaps_acknowledged}")
            self.lines.append(f"• Result: {result.result}")
        
        elif isinstance(result, MessageDeliveryResult):
            self.lines.append(f"• Channel: {result.channel}")
            self.lines.append(f"• Recipient: {result.recipient}")
            if result.cc:
                self.lines.append(f"• CC: {', '.join(result.cc)}")
            self.lines.append(f"• Delivery Status: {result.delivery_status}")
    
    def _add_footer(self):
        """Add map footer"""
        self.lines.append("=" * 74)
    
    def render(
        self,
        task_plan: L1TaskPlan,
        routing_results: List[L2RoutingResult]
    ) -> str:
        """
        Render the complete orchestration map.
        
        Args:
            task_plan: The L1 task plan
            routing_results: The L2 routing results with extractions
            
        Returns:
            Formatted text map
        """
        self.lines = []
        self.message = task_plan.source_message
        
        self._add_header()
        self._add_task_plan(task_plan)
        self._add_execution_results(routing_results)
        self._add_footer()
        
        return "\n".join(self.lines)


def render_orchestration_map(
    task_plan: L1TaskPlan,
    routing_results: List[L2RoutingResult]
) -> str:
    """
    Convenience function to render an orchestration map.
    
    Args:
        task_plan: The L1 task plan
        routing_results: L2 routing results
        
    Returns:
        Formatted map text
    """
    renderer = OrchestrationMapRenderer()
    return renderer.render(task_plan, routing_results)
