
# Mock responses for Demo/Presentation purposes when API is rate limited

SAMPLE_L1_RESPONSE = """
{
  "tasks": [
    {
      "task_id": "TSK-001",
      "description": "Analyze feasibility of real-time notifications",
      "assigned_to": "Engineer",
      "priority": "High",
      "domain": "action_item_extraction",
      "dependencies": []
    },
    {
      "task_id": "TSK-002",
      "description": "Estimate effort for dashboard export feature",
      "assigned_to": "Engineer",
      "priority": "Medium",
      "domain": "action_item_extraction",
      "dependencies": []
    },
    {
      "task_id": "TSK-003",
      "description": "Assess timeline impact of new scope (20% budget increase)",
      "assigned_to": "Product Manager",
      "priority": "High",
      "domain": "risk_extraction",
      "dependencies": ["TSK-001", "TSK-002"]
    }
  ]
}
"""

SAMPLE_SIDEBAR_RESPONSE = """
{
  "tasks": [
    {
      "task_id": "TSK-101",
      "description": "Prepare sidebar deployment checklist",
      "assigned_to": "DevOps",
      "priority": "High",
      "domain": "action_item_extraction",
      "dependencies": []
    },
    {
      "task_id": "TSK-102",
      "description": "Verify RBAC for new sidebar endpoints",
      "assigned_to": "Security",
      "priority": "High",
      "domain": "risk_extraction",
      "dependencies": []
    }
  ]
}
"""

def get_mock_response(user_prompt: str):
    """Return a mock response based on prompt content"""
    prompt_lower = user_prompt.lower()
    
    # Match the detailed sample message
    if "notifications" in prompt_lower and "dashboard export" in prompt_lower:
        return SAMPLE_L1_RESPONSE
        
    # Match the sidebar test
    if "sidebar" in prompt_lower and "deploy" in prompt_lower:
        return SAMPLE_SIDEBAR_RESPONSE
        
    # Default generic fallback
    return """
    {
      "tasks": [
        {
          "task_id": "TSK-GEN-001",
          "description": "Process user request (Fallback Mode)",
          "assigned_to": "System",
          "priority": "Medium",
          "domain": "decision_extraction",
          "dependencies": []
        }
      ]
    }
    """
