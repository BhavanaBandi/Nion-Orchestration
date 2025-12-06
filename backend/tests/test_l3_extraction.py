# Tests for L3 Extraction Agents
import pytest
from unittest.mock import patch, AsyncMock

from models.l3_models import ActionItemsResult, RisksResult, DecisionsResult
from orchestration.l3_agents import action_items_agent, risks_agent, decisions_agent
from orchestration.l3_agents.action_items import ActionItemsAgent
from orchestration.l3_agents.risks import RisksAgent
from orchestration.l3_agents.decisions import DecisionsAgent


class TestActionItemsAgent:
    """Tests for action items extraction"""
    
    @pytest.mark.asyncio
    async def test_extract_single_action(self, mock_grok_action_items_response):
        """Test extracting a single action item"""
        mock_client = AsyncMock()
        mock_client.complete.return_value = mock_grok_action_items_response
        
        agent = ActionItemsAgent()
        agent.client = mock_client
        
        result = await agent.extract("John needs to complete the API documentation by Friday")
        
        assert isinstance(result, ActionItemsResult)
        assert len(result.items) == 1
        assert result.items[0].action == "Complete API documentation"
        assert result.items[0].owner == "John"
        assert result.items[0].deadline == "Friday"
    
    @pytest.mark.asyncio
    async def test_empty_content_returns_empty(self):
        """Test that empty content returns empty result"""
        agent = ActionItemsAgent()
        result = await agent.extract("")
        
        assert isinstance(result, ActionItemsResult)
        assert result.items == []
    
    @pytest.mark.asyncio
    async def test_malformed_response_fallback(self):
        """Test graceful handling of malformed responses"""
        mock_client = AsyncMock()
        mock_client.complete.return_value = "This is not valid JSON"
        
        agent = ActionItemsAgent()
        agent.client = mock_client
        
        result = await agent.extract("Some content")
        
        assert isinstance(result, ActionItemsResult)
        assert result.items == []  # Graceful fallback


class TestRisksAgent:
    """Tests for risks extraction"""
    
    @pytest.mark.asyncio
    async def test_extract_risk(self, mock_grok_risks_response):
        """Test extracting a risk"""
        mock_client = AsyncMock()
        mock_client.complete.return_value = mock_grok_risks_response
        
        agent = RisksAgent()
        agent.client = mock_client
        
        result = await agent.extract("Risk: Payment integration blocked on vendor approval")
        
        assert isinstance(result, RisksResult)
        assert len(result.items) == 1
        assert result.items[0].severity == "high"
        assert "blocked" in result.items[0].description.lower()
    
    @pytest.mark.asyncio
    async def test_empty_content_returns_empty(self):
        """Test that empty content returns empty result"""
        agent = RisksAgent()
        result = await agent.extract("")
        
        assert isinstance(result, RisksResult)
        assert result.items == []


class TestDecisionsAgent:
    """Tests for decisions extraction"""
    
    @pytest.mark.asyncio
    async def test_extract_decision(self, mock_grok_decisions_response):
        """Test extracting a decision"""
        mock_client = AsyncMock()
        mock_client.complete.return_value = mock_grok_decisions_response
        
        agent = DecisionsAgent()
        agent.client = mock_client
        
        result = await agent.extract("Decision: We're moving to weekly deploys")
        
        assert isinstance(result, DecisionsResult)
        assert len(result.items) == 1
        assert "weekly deploys" in result.items[0].decision.lower()
    
    @pytest.mark.asyncio
    async def test_empty_content_returns_empty(self):
        """Test that empty content returns empty result"""
        agent = DecisionsAgent()
        result = await agent.extract("")
        
        assert isinstance(result, DecisionsResult)
        assert result.items == []


class TestL3ModelValidation:
    """Test Pydantic model validation for L3 results"""
    
    def test_action_item_defaults(self):
        """Test ActionItem default values"""
        from models.l3_models import ActionItem
        
        item = ActionItem(action="Test action")
        assert item.status == "pending"
        assert item.owner is None
        assert item.deadline is None
    
    def test_risk_defaults(self):
        """Test Risk default values"""
        from models.l3_models import Risk
        
        risk = Risk(description="Test risk")
        assert risk.severity == "medium"
        assert risk.mitigation is None
    
    def test_decision_defaults(self):
        """Test Decision default values"""
        from models.l3_models import Decision
        
        decision = Decision(decision="Test decision")
        assert decision.rationale is None
        assert decision.made_by is None
