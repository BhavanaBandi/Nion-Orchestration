from typing import Dict, Any, List, Optional

# Permission Matrix
PERMISSIONS = {
    "project_manager": ["*"],  # Wildcard: Access everything
    "engineer": [
        "view_orchestration_map",
        "view_internal_l1_tasks",
        "view_internal_l2_routing",
        "view_internal_l3_outputs",
        "view_risks",
        "view_decisions",
        "view_timeline_analysis",
        "view_final_response",
        "view_sensitive_logs"
    ],
    "designer": [
        "view_orchestration_map",
        "view_internal_l1_tasks",
        "view_risks",
        "view_decisions",
        "view_timeline_analysis",
        "view_final_response"
    ],
    "vp_engineering": [
        "view_orchestration_map",
        "view_risks",
        "view_decisions",
        "view_timeline_analysis",
        "view_final_response"
    ],
    "customer": [
        "view_final_response"
        # No internal views
    ],
    "viewer": [
        "view_final_response"
    ]
}

def has_permission(role: str, permission: str) -> bool:
    """Check if role has specific permission."""
    perms = PERMISSIONS.get(role, [])
    if "*" in perms:
        return True
    return permission in perms

def filter_response(data: Dict[str, Any], role: str) -> Dict[str, Any]:
    """
    Filter the orchestration response based on user role.
    """
    if role == "project_manager":
        return data  # No filtering for PM
    
    # Clone data to avoid mutating original if needed (though here we just return new dict)
    filtered = data.copy()
    
    # 1. Customer Sanitization (Special Case)
    if role == "customer":
        return generate_customer_summary(data)
    
    # 2. General Filtering for internal roles
    # If they can't view the map, redact it
    if not has_permission(role, "view_orchestration_map"):
        filtered["orchestration_map"] = "[REDACTED: Insufficient Permissions]"
        
    # Note: currently our OrchestrationResponse is flat. 
    # If it had nested "l1_tasks" etc, we would filter those keys here.
    # For MVP, the main "internal details" act is the orchestration map text itself.
    
    return filtered

def generate_customer_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a sanitized summary for customers.
    """
    message_id = data.get("message_id", "Unknown")
    # Try to extract the final response from the map if possible, 
    # or just provide a generic status.
    # Since the map is unstructured text, extracting the "Response" without L3 structured data is hard 
    # unless we change the API to return structured L3 outputs too.
    # For MVP, we will return a polite summary.
    
    return {
        "message_id": message_id,
        "status": "Processed",
        "customer_view": True,
        "summary": "Your request has been processed by the Nion Orchestration Engine.",
        "final_response": "Please contact your Project Manager for the full detailed report." 
        # In a real system, we'd extract the specific L3:qna response here.
    }
