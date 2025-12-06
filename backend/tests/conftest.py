# Test configuration and fixtures
import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Ensure we can import from the parent directory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_message():
    """Sample message for testing"""
    return {
        "id": "MSG-TEST-001",
        "body": """Team, following yesterday's sprint review:

1. John needs to complete the API documentation by Friday
2. Risk: The payment integration is blocked on vendor approval
3. Decision: We're moving to weekly deploys starting next sprint

Please update your trackers accordingly."""
    }


@pytest.fixture
def mock_grok_l1_response():
    """Mock L1 response from Grok"""
    return '''{
    "tasks": [
        {
            "task_id": "TASK-001",
            "domain": "TRACKING_EXECUTION",
            "description": "Extract action item: API documentation by Friday (owner: John)",
            "priority": "high"
        },
        {
            "task_id": "TASK-002",
            "domain": "TRACKING_EXECUTION",
            "description": "Extract risk: Payment integration blocked on vendor approval",
            "priority": "high"
        },
        {
            "task_id": "TASK-003",
            "domain": "LEARNING_IMPROVEMENT",
            "description": "Record decision: Moving to weekly deploys next sprint",
            "priority": "medium"
        }
    ]
}'''


@pytest.fixture
def mock_grok_action_items_response():
    """Mock action items extraction response"""
    return '''{
    "items": [
        {
            "action": "Complete API documentation",
            "owner": "John",
            "deadline": "Friday",
            "status": "pending"
        }
    ]
}'''


@pytest.fixture
def mock_grok_risks_response():
    """Mock risks extraction response"""
    return '''{
    "items": [
        {
            "description": "Payment integration blocked on vendor approval",
            "severity": "high",
            "mitigation": "Escalate to management",
            "owner": null
        }
    ]
}'''


@pytest.fixture
def mock_grok_decisions_response():
    """Mock decisions extraction response"""
    return '''{
    "items": [
        {
            "decision": "Moving to weekly deploys starting next sprint",
            "rationale": "Improve deployment frequency",
            "made_by": "Team",
            "effective_date": "Next sprint"
        }
    ]
}'''


@pytest.fixture
def mock_grok_client():
    """Create a mock Grok client"""
    mock = AsyncMock()
    return mock
