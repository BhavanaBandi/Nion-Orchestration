# Nion Orchestration Engine - FastAPI Backend
# API server for frontend integration

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Nion Orchestration API",
        "version": "0.2.0"
    }


@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(request: OrchestrationRequest):
    """
    Main orchestration endpoint.
    
    Processes a message through the L1→L2→L3 pipeline.
    """
    message_id = request.message_id or f"MSG-{int(datetime.now().timestamp())}"
    
    logger.info(f"Processing orchestration request: {message_id}")
    
    try:
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
        storage.save_orchestration_map(message_id, map_text)
        
        return OrchestrationResponse(
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            orchestration_map=map_text,
            task_count=len(task_plan.tasks),
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        return OrchestrationResponse(
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            orchestration_map="",
            task_count=0,
            success=False,
            error=str(e)
        )


@app.get("/history")
async def get_history(limit: int = 10):
    """Get recent orchestration history"""
    # For MVP, return empty list (can be expanded)
    return {"maps": [], "total": 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
