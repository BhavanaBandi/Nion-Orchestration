# Tests for Orchestration Map Rendering
import pytest
from datetime import datetime

from models.l1_models import L1Task, L1TaskPlan
from models.l3_models import (
    ActionItem, ActionItemsResult,
    Risk, RisksResult,
    Decision, DecisionsResult
)
from orchestration.l2_coordinator import L2RoutingResult
from rendering.map_renderer import OrchestrationMapRenderer, render_orchestration_map


class TestMapRendering:
    """Tests for orchestration map rendering"""
    
    def test_render_with_action_items(self):
        """Test rendering with action items"""
        task_plan = L1TaskPlan(
            tasks=[
                L1Task(
                    task_id="TASK-001",
                    domain="TRACKING_EXECUTION",
                    description="Test task",
                    priority="high"
                )
            ],
            source_message_id="MSG-001"
        )
        
        action_items = ActionItemsResult(items=[
            ActionItem(action="Task 1", owner="Alice", status="pending"),
            ActionItem(action="Task 2", owner="Bob", status="done")
        ])
        
        routing_results = [
            L2RoutingResult(
                task=task_plan.tasks[0],
                domain="TRACKING_EXECUTION",
                extraction_result=action_items,
                success=True
            )
        ]
        
        output = render_orchestration_map("MSG-001", task_plan, routing_results)
        
        assert "ORCHESTRATION MAP" in output
        assert "Task 1" in output
        assert "Alice" in output
        assert "TASK-001" in output
    
    def test_render_with_risks(self):
        """Test rendering with risks"""
        task_plan = L1TaskPlan(tasks=[], source_message_id="MSG-001")
        
        risks = RisksResult(items=[
            Risk(description="Critical blocker", severity="high", mitigation="Escalate")
        ])
        
        routing_results = [
            L2RoutingResult(
                task=L1Task(task_id="TASK-001", domain="TRACKING_EXECUTION", description="Test"),
                domain="TRACKING_EXECUTION",
                extraction_result=risks,
                success=True
            )
        ]
        
        output = render_orchestration_map("MSG-001", task_plan, routing_results)
        
        assert "RISKS" in output
        assert "Critical blocker" in output
        assert "HIGH" in output
        assert "Escalate" in output
    
    def test_render_with_decisions(self):
        """Test rendering with decisions"""
        task_plan = L1TaskPlan(tasks=[], source_message_id="MSG-001")
        
        decisions = DecisionsResult(items=[
            Decision(
                decision="Use new framework",
                rationale="Better performance",
                made_by="Team"
            )
        ])
        
        routing_results = [
            L2RoutingResult(
                task=L1Task(task_id="TASK-001", domain="LEARNING_IMPROVEMENT", description="Test"),
                domain="LEARNING_IMPROVEMENT",
                extraction_result=decisions,
                success=True
            )
        ]
        
        output = render_orchestration_map("MSG-001", task_plan, routing_results)
        
        assert "DECISIONS" in output
        assert "Use new framework" in output
        assert "Better performance" in output
    
    def test_render_empty_map(self):
        """Test rendering with no data"""
        task_plan = L1TaskPlan(tasks=[], source_message_id="MSG-001")
        routing_results = []
        
        output = render_orchestration_map("MSG-001", task_plan, routing_results)
        
        assert "ORCHESTRATION MAP" in output
        assert "MSG-001" in output
        assert "No tasks identified" in output
    
    def test_output_is_valid_text(self):
        """Test that output is valid string"""
        task_plan = L1TaskPlan(tasks=[], source_message_id="MSG-001")
        
        output = render_orchestration_map("MSG-001", task_plan, [])
        
        assert isinstance(output, str)
        assert len(output) > 0
    
    def test_render_handles_failed_routing(self):
        """Test that failed routing results are handled gracefully"""
        task_plan = L1TaskPlan(
            tasks=[
                L1Task(task_id="TASK-001", domain="TRACKING_EXECUTION", description="Test")
            ]
        )
        
        routing_results = [
            L2RoutingResult(
                task=task_plan.tasks[0],
                domain="TRACKING_EXECUTION",
                extraction_result=None,  # Failed extraction
                success=False,
                error="API Error"
            )
        ]
        
        # Should not raise
        output = render_orchestration_map("MSG-001", task_plan, routing_results)
        assert "ORCHESTRATION MAP" in output


class TestRendererClass:
    """Test OrchestrationMapRenderer class directly"""
    
    def test_renderer_initialization(self):
        """Test renderer initialization"""
        renderer = OrchestrationMapRenderer("MSG-001")
        assert renderer.message_id == "MSG-001"
        assert renderer.lines == []
    
    def test_section_headers(self):
        """Test section header formatting"""
        renderer = OrchestrationMapRenderer("MSG-001")
        renderer._add_section("TEST SECTION")
        
        assert "TEST SECTION" in renderer.lines
        assert "-" * 40 in renderer.lines
