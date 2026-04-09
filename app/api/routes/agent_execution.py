from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas
from app.services import agent_execution_service
from app.api.deps import get_db, get_tenant

router = APIRouter()

@router.post("/agents/{agent_id}/run", response_model=schemas.AgentRunResponse, tags=["Agent Execution"], summary="Run an agent", description="Run an agent with a task and model. Handles multi-step tool calls and returns the final response.")
def run_agent(agent_id: int, run: schemas.AgentRunRequest, db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    result = agent_execution_service.run_agent(db, tenant.id, agent_id, run)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result

@router.get("/agents/{agent_id}/executions", response_model=List[schemas.AgentExecution], tags=["Agent Execution"], summary="List agent executions", description="List execution history for an agent with pagination.")
def list_agent_executions(agent_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    return agent_execution_service.get_agent_executions(db, tenant.id, agent_id, skip, limit)
