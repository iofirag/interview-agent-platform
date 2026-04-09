from sqlalchemy.orm import Session
from typing import Optional
from app.db.repositories import tool_repo
from app.db.repositories import agent_repo

def create_tool(db: Session, tenant_id: int, name: str, description: str):
    return tool_repo.create_tool(db, tenant_id, name, description)

def get_tools(db: Session, tenant_id: int, agent_name: Optional[str] = None):
    if agent_name:
        agent = agent_repo.get_agent_by_name(db, tenant_id, agent_name)
        if not agent:
            return []
        return tool_repo.get_tools_by_agent(db, tenant_id, agent.id)
    return tool_repo.get_tools(db, tenant_id)

def update_tool(db: Session, tenant_id: int, tool_id: int, name: str, description: str):
    return tool_repo.update_tool(db, tenant_id, tool_id, name, description)

def delete_tool(db: Session, tenant_id: int, tool_id: int):
    return tool_repo.delete_tool(db, tenant_id, tool_id)
