
from fastapi import FastAPI
from app.api.routes import tools_router, agents_router, agent_execution_router, health_router
from app.core.lifespan import lifespan

app = FastAPI(
    title="Mini Agent Platform API",
    description="Backend API for managing multi-tenant AI agents, tools, and executions.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Tools", "description": "CRUD operations for tools."},
        {"name": "Agents", "description": "CRUD operations for agents."},
        {"name": "Agent Execution", "description": "Run agents and view execution history."},
        {"name": "Health", "description": "Health check endpoint."},
    ],
    lifespan=lifespan
)

app.include_router(tools_router)
app.include_router(agents_router)
app.include_router(agent_execution_router)
app.include_router(health_router)