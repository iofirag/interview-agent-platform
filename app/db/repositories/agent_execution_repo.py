import json
from sqlalchemy.orm import Session
from app.db.models import AgentExecution

def create_agent_execution(db: Session, agent_id, tenant_id, model, prompt, tool_calls, final_response):
    execution = AgentExecution(
        agent_id=agent_id,
        tenant_id=tenant_id,
        model=model,
        prompt=prompt,
        tool_calls=json.dumps(tool_calls, ensure_ascii=False),
        final_response=final_response
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution

def get_agent_executions(db: Session, tenant_id: int, agent_id: int = None, skip: int = 0, limit: int = 20):
    q = db.query(AgentExecution).filter(AgentExecution.tenant_id == tenant_id)
    if agent_id:
        q = q.filter(AgentExecution.agent_id == agent_id)
    return q.order_by(AgentExecution.timestamp.desc()).offset(skip).limit(limit).all()
