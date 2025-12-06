# Tests for L1 Planner
import pytest
from unittest.mock import patch, AsyncMock

from models.l1_models import L1Task, L1TaskPlan
from orchestration.l1_orchestrator import L1Orchestrator
from llm.grok_client import GrokClient


class TestL1Parsing:
    """Test L1 response parsing without calling Grok."""
    
    def test_parse_valid_json(self, mock_grok_l1_response):
        """Test parsing a valid JSON response"""
        orchestrator = L1Orchestrator()
        result = orchestrator._parse_response(mock_grok_l1_response, "MSG-001")
        
        assert len(result.tasks) == 3
        assert result.tasks[0].task_id == "TASK-001"
        assert result.tasks[0].domain == "TRACKING_EXECUTION"
        assert result.tasks[0].priority == "high"
    
    def test_parse_json_in_markdown(self):
        """Test parsing JSON wrapped in markdown code block"""
        raw = '''```json
{"tasks": [{"task_id": "TASK-001", "domain": "TRACKING_EXECUTION", "description": "Test task", "priority": "medium"}]}
```'''
        orchestrator = L1Orchestrator()
        result = orchestrator._parse_response(raw, "MSG-001")
        
        assert len(result.tasks) == 1
        assert result.tasks[0].description == "Test task"
    
    def test_parse_empty_tasks(self):
        """Test parsing response with no tasks"""
        raw = '{"tasks": []}'
        orchestrator = L1Orchestrator()
        result = orchestrator._parse_response(raw, "MSG-001")
        
        assert result.tasks == []
    
    def test_parse_invalid_returns_empty(self):
        """Test that invalid JSON returns empty plan"""
        raw = "This is not JSON at all"
        orchestrator = L1Orchestrator()
        result = orchestrator._parse_response(raw, "MSG-001")
        
        assert result.tasks == []
    
    def test_invalid_domain_skipped(self):
        """Test that tasks with invalid domains are skipped"""
        raw = '{"tasks": [{"task_id": "TASK-001", "domain": "INVALID_DOMAIN", "description": "Test"}]}'
        orchestrator = L1Orchestrator()
        result = orchestrator._parse_response(raw, "MSG-001")
        
        # Invalid task should be skipped
        assert len(result.tasks) == 0
    
    def test_missing_required_fields_skipped(self):
        """Test that tasks missing required fields are skipped"""
        raw = '{"tasks": [{"task_id": "TASK-001"}]}'  # Missing domain and description
        orchestrator = L1Orchestrator()
        result = orchestrator._parse_response(raw, "MSG-001")
        
        assert len(result.tasks) == 0


class TestL1Integration:
    """Integration tests with mocked Grok responses."""
    
    @pytest.mark.asyncio
    async def test_plan_tasks_success(self, mock_grok_l1_response):
        """Test successful task planning"""
        mock_client = AsyncMock()
        mock_client.complete.return_value = mock_grok_l1_response
        
        orchestrator = L1Orchestrator(client=mock_client)
        result = await orchestrator.plan_tasks("Sample message", "MSG-001")
        
        assert result.success is True
        assert len(result.task_plan.tasks) == 3
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_plan_tasks_api_error(self):
        """Test handling of API errors"""
        mock_client = AsyncMock()
        mock_client.complete.side_effect = Exception("API Error")
        
        orchestrator = L1Orchestrator(client=mock_client)
        result = await orchestrator.plan_tasks("Sample message", "MSG-001")
        
        assert result.success is False
        assert result.error is not None
        assert "API Error" in result.error


class TestGrokJsonExtraction:
    """Test JSON extraction from various response formats"""
    
    def test_extract_direct_json(self):
        """Test extraction of direct JSON"""
        raw = '{"key": "value"}'
        result = GrokClient.extract_json(raw)
        assert result == {"key": "value"}
    
    def test_extract_from_markdown(self):
        """Test extraction from markdown code block"""
        raw = '''Here is my response:
```json
{"key": "value"}
```
That's it!'''
        result = GrokClient.extract_json(raw)
        assert result == {"key": "value"}
    
    def test_extract_embedded_json(self):
        """Test extraction of embedded JSON"""
        raw = 'Here is the result: {"key": "value"} and more text'
        result = GrokClient.extract_json(raw)
        assert result == {"key": "value"}
    
    def test_extract_array(self):
        """Test extraction of JSON array"""
        raw = '[{"a": 1}, {"b": 2}]'
        result = GrokClient.extract_json(raw)
        assert result == [{"a": 1}, {"b": 2}]
    
    def test_extract_failure(self):
        """Test that extraction raises on no JSON"""
        raw = "No JSON here at all"
        with pytest.raises(ValueError):
            GrokClient.extract_json(raw)
