from sqlalchemy.orm import Session
from app.db.models import Tool, AgentTool, Agent

def create_tool(db: Session, tenant_id: int, name: str, description: str):
    tool = Tool(tenant_id=tenant_id, name=name, description=description)
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool

def get_tools(db: Session, tenant_id: int, agent_name: str = None):
    q = db.query(Tool).filter(Tool.tenant_id == tenant_id)
    if agent_name:
        q = q.join(AgentTool).join(Agent).filter(Agent.name == agent_name)
    return q.all()

def get_tool(db: Session, tenant_id: int, tool_id: int):
    return db.query(Tool).filter(Tool.tenant_id == tenant_id, Tool.id == tool_id).first()

def update_tool(db: Session, tenant_id: int, tool_id: int, name: str, description: str):
    tool = get_tool(db, tenant_id, tool_id)
    if tool:
        tool.name = name
        tool.description = description
        db.commit()
        db.refresh(tool)
    return tool

def delete_tool(db: Session, tenant_id: int, tool_id: int):
    tool = get_tool(db, tenant_id, tool_id)
    if tool:
        db.delete(tool)
        db.commit()
    return tool

def fetch_agent_tools(db: Session, agent):
    """
    Fetch tools for the given agent from the database.
    Returns a dict of tool name to tool object.
    """
    tool_links = agent.tools or []
    tool_ids = [at.tool_id for at in tool_links]
    tools = []
    if tool_ids:
        tools = db.query(Tool)\
            .filter(Tool.id.in_(tool_ids))\
            .all()
    return {t.name: t for t in tools}