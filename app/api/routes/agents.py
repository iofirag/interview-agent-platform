from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.services import agent_service
from app.api.deps import get_db, get_tenant

router = APIRouter()

@router.post("/agents", response_model=schemas.Agent, tags=["Agents"], summary="Create an agent", description="Create a new agent for the tenant.")
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    return agent_service.create_agent(db, tenant.id, agent.name, agent.role, agent.description, agent.tool_ids)

@router.get("/agents", response_model=List[schemas.Agent], tags=["Agents"], summary="List agents", description="List all agents for the tenant. Optionally filter by tool name.")
def list_agents(tool_name: Optional[str] = Query(None), db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    return agent_service.get_agents(db, tenant.id, tool_name)

@router.put("/agents/{agent_id}", response_model=schemas.Agent, tags=["Agents"], summary="Update an agent", description="Update an existing agent.")
def update_agent(agent_id: int, agent: schemas.AgentCreate, db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    updated = agent_service.update_agent(db, tenant.id, agent_id, agent.name, agent.role, agent.description, agent.tool_ids)
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found")
    return updated

@router.delete("/agents/{agent_id}", tags=["Agents"], summary="Delete an agent", description="Delete an agent by ID.")
def delete_agent(agent_id: int, db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    deleted = agent_service.delete_agent(db, tenant.id, agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"ok": True}
