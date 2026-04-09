from sqlalchemy.orm import Session
from app.db.models import Agent, AgentTool, Tool

def create_agent(db: Session, tenant_id: int, name: str, role: str, description: str, tool_ids: list):
    agent = Agent(tenant_id=tenant_id, name=name, role=role, description=description)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    for tool_id in tool_ids:
        at = AgentTool(agent_id=agent.id, tool_id=tool_id)
        db.add(at)
    db.commit()
    db.refresh(agent)
    return agent

def get_agents(db: Session, tenant_id: int, tool_name: str = None):
    q = db.query(Agent).filter(Agent.tenant_id == tenant_id)
    if tool_name:
        q = q.join(AgentTool).join(Tool).filter(Tool.name == tool_name)
    return q.all()

def get_agent(db: Session, tenant_id: int, agent_id: int):
    return db.query(Agent).filter(Agent.tenant_id == tenant_id, Agent.id == agent_id).first()

def update_agent(db: Session, tenant_id: int, agent_id: int, name: str, role: str, description: str, tool_ids: list):
    agent = get_agent(db, tenant_id, agent_id)
    if agent:
        agent.name = name
        agent.role = role
        agent.description = description
        db.query(AgentTool).filter(AgentTool.agent_id == agent_id).delete()
        for tool_id in tool_ids:
            at = AgentTool(agent_id=agent_id, tool_id=tool_id)
            db.add(at)
        db.commit()
        db.refresh(agent)
    return agent

def delete_agent(db: Session, tenant_id: int, agent_id: int):
    agent = get_agent(db, tenant_id, agent_id)
    if agent:
        db.query(AgentTool).filter(AgentTool.agent_id == agent_id).delete()
        db.delete(agent)
        db.commit()
    return agent
