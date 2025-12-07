# Nion Orchestration Engine - FastAPI Backend
# API server for frontend integration

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from rag.api import router as rag_router
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from orchestration.l1_orchestrator import L1Orchestrator
from orchestration.l2_coordinator import L2Coordinator
from rendering.map_renderer import render_orchestration_map
from storage.db import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Nion Orchestration API",
    description="L1→L2→L3 Task Orchestration Engine",
    version="0.2.0"
)

# Add CORS middleware for frontend
# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(rag_router, prefix="/rag")

# Authentication logic
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, status
import auth

import rbac
from auth import User, get_user_role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    username = auth.verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    role = get_user_role(username)
    return User(username=username, role=role)


# Request/Response Models
class Sender(BaseModel):
    name: str = "Unknown"
    role: Optional[str] = None


class OrchestrationRequest(BaseModel):
    message_id: Optional[str] = None
    source: str = "email"
    sender: Sender
    content: str
    project: Optional[str] = None


class OrchestrationResponse(BaseModel):
    message_id: str
    timestamp: str
    orchestration_map: str
    task_count: int
    success: bool
    error: Optional[str] = None
    # Flexible extra fields for sanitized views (e.g. summary)
    extra: Optional[dict] = None

    class Config:
        extra = "allow" 


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Nion Orchestration API",
        "version": "0.2.0"
    }


@app.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_ok = auth.verify_password(form_data.password, auth.ADMIN_PASSWORD_HASH)
    # Check against hardcoded admin OR allow any user in USER_ROLES for testing if password matches
    # For MVP, let's stick to simple logic: 
    # If username is in USER_ROLES, we allow login with the admin password for simplicity? 
    # Or just allow 'admin' properly. 
    # To test other roles, we need a way to login as them.
    # Hack for MVP: IF username in USER_ROLES, we accept the password "password123" (which is what hash matches).
    
    # Verify password first (same password for everyone in MVP demo)
    if not user_ok:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Allow login if they are in our mock DB (or if they are the admin hardcoded var)
    known_user = form_data.username == auth.ADMIN_USER or form_data.username in auth.USER_ROLES
    if not known_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown user",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = auth.create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Project Endpoints ---

class ProjectCreate(BaseModel):
    name: str

@app.get("/projects")
async def list_projects(current_user: User = Depends(get_current_user)):
    """List all projects"""
    # Filter for customer if needed, but for MVP let's show all for internal users
    if current_user.role == "customer":
        # MVP: Customers might only see projects they are assigned to, or none.
        # For now, return all (or filtered). Let's return all for "demo" visibility.
        pass 
    
    return storage.list_projects()

@app.post("/projects")
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    # Only Admin/PM/Engineer should create projects?
    if current_user.role == "customer":
        raise HTTPException(status_code=403, detail="Not authorized to create projects")
        
    project_id = storage.create_project(project.name)
    return {"id": project_id, "name": project.name, "success": True}

@app.get("/projects/{project_id}/history")
async def get_project_history(
    project_id: int, 
    current_user: User = Depends(get_current_user)
):
    """Get orchestration history for a specific project"""
    return storage.get_project_history(project_id)


# --- Orchestration ---

@app.post("/orchestrate")  # Return dict for flexibility with RBAC
async def orchestrate(
    request: OrchestrationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Main orchestration endpoint.
    Protected by JWT Authentication + RBAC.
    """
    message_id = request.message_id or f"MSG-{int(datetime.now().timestamp())}"
    
    logger.info(f"Processing request {message_id} from {current_user.username} (Role: {current_user.role}, Project: {request.project})")

    try:
        # Resolve Project ID if provided as name or ID
        project_id = None
        if request.project:
            # Try to lookup project ID from name if string is passed
            # For MVP, let's assumes the frontend sends the project ID in request.project if it's an ID, or we handle string names?
            # The storage `create_project` returns an ID. The frontend calls `orchestrate` with `project`.
            # If `request.project` is a string like "PRJ-ALPHA", we might want to get its ID or create it?
            # Actually, per design, the sidebar sends the selected `project_id`.
            # Let's try to interpret request.project as ID first.
            try:
                project_id = int(request.project)
            except ValueError:
                # It's a name, maybe legacy or user typed it in.
                # Let's create-or-get.
                project_id = storage.create_project(request.project)
        
        # Build message dict
        message_dict = {
            "message_id": message_id,
            "source": request.source,
            "sender": {
                "name": request.sender.name,
                "role": request.sender.role
            },
            "content": request.content,
            "project": request.project
        }
        
        # L1: Plan tasks
        logger.info("L1: Planning tasks...")
        l1_orchestrator = L1Orchestrator()
        l1_result = await l1_orchestrator.plan_tasks_from_dict(message_dict)
        
        if not l1_result.success:
            raise HTTPException(
                status_code=500,
                detail=f"L1 planning failed: {l1_result.error}"
            )
        
        task_plan = l1_result.task_plan
        logger.info(f"L1: Generated {len(task_plan.tasks)} tasks")
        
        # Save task plan
        storage.save_task_plan(task_plan)
        
        # L2: Route and execute
        logger.info("L2: Routing tasks...")
        l2_coordinator = L2Coordinator()
        routing_results = await l2_coordinator.route_all_tasks(
            task_plan, 
            request.content
        )
        
        # Save extractions
        for result in routing_results:
            if result.success and result.extraction_result:
                storage.save_extraction(
                    task_id=result.task.task_id,
                    extraction_type=result.l3_agent or result.domain,
                    data=result.extraction_result.model_dump(mode='json')
                )
        
        # Render map
        map_text = render_orchestration_map(task_plan, routing_results)
        
        # Save with Project ID
        storage.save_orchestration_map(message_id, map_text, project_id=project_id)
        
        # Aggregate Structured Data
        action_items = []
        risks = []
        decisions = []
        
        for result in routing_results:
            if result.success and result.extraction_result:
                data = result.extraction_result.model_dump(mode='json')
                
                # Check for "items" list which is common pattern in our extraction models
                if "items" in data:
                    items = data["items"]
                    if result.l3_agent == "action_item_extraction":
                        action_items.extend(items)
                    elif result.l3_agent == "risk_extraction":
                        risks.extend(items)
                    elif result.l3_agent == "decision_extraction":
                        decisions.extend(items)
                        
        raw_response = {
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            "orchestration_map": map_text,
            "task_count": len(task_plan.tasks),
            "success": True,
            "extra": {
                "action_items": action_items,
                "risks": risks,
                "decisions": decisions
            }
        }
        
        # Apply RBAC Filter
        return rbac.filter_response(raw_response, current_user.role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        error_response = {
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            "orchestration_map": "",
            "task_count": 0,
            "success": False,
            "error": str(e)
        }
        return rbac.filter_response(error_response, current_user.role)


@app.get("/history")
async def get_history(limit: int = 10):
    """Get recent orchestration history"""
    # For MVP, return empty list (can be expanded)
    return {"maps": [], "total": 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
