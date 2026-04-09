from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.repositories import agent_repo

def create_agent(db: Session, tenant_id: int, name: str, role: str, description: str, tool_ids: List[int]):
    return agent_repo.create_agent(db, tenant_id, name, role, description, tool_ids)

def get_agents(db: Session, tenant_id: int, tool_name: Optional[str] = None):
    return agent_repo.get_agents(db, tenant_id, tool_name)

def update_agent(db: Session, tenant_id: int, agent_id: int, name: str, role: str, description: str, tool_ids: List[int]):
    return agent_repo.update_agent(db, tenant_id, agent_id, name, role, description, tool_ids)

def delete_agent(db: Session, tenant_id: int, agent_id: int):
    return agent_repo.delete_agent(db, tenant_id, agent_id)
