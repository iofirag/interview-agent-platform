from sqlalchemy.orm import Session
from app.db.repositories import agent_execution_repo, agent_repo, tool_repo
from app.services import llm_service

def run_agent(db: Session, tenant_id: int, agent_id: int, run_request):
    agent = agent_repo.get_agent(db, tenant_id, agent_id)
    if not agent:
        return None
    agent_tools = tool_repo.fetch_agent_tools(db, agent)
    agent_tool_names = list(agent_tools.keys())
    llm_service_result = llm_service.run_agent(run_request, agent, agent_tool_names)
    agent_execution_repo.create_agent_execution(
        db=db,
        agent_id=agent.id,
        tenant_id=agent.tenant_id,
        model=run_request.model,
        prompt=llm_service_result["prompt"],
        tool_calls=llm_service_result["tool_calls"],
        final_response=llm_service_result["final_response"]
    )
    return {
        "final_response": llm_service_result["final_response"],
        "tool_calls": llm_service_result["tool_calls"],
        "prompt": llm_service_result["prompt"]
    }

def get_agent_executions(db: Session, tenant_id: int, agent_id: int, skip: int = 0, limit: int = 20):
    return agent_execution_repo.get_agent_executions(db, tenant_id, agent_id, skip, limit)
