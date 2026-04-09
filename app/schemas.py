import datetime
from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.core.config import settings


class ToolBase(BaseModel):
    name: str
    description: str


class ToolCreate(ToolBase):
    pass


class Tool(ToolBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AgentBase(BaseModel):
    name: str
    role: str
    description: str


class AgentCreate(AgentBase):
    tool_ids: List[int] = Field(default_factory=list)


class Agent(AgentBase):
    id: int
    tool_ids: List[int] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class AgentExecution(BaseModel):
    id: int
    agent_id: int
    tenant_id: int
    model: str
    prompt: str
    tool_calls: Optional[str]
    final_response: Optional[str]
    timestamp: datetime.datetime
    model_config = ConfigDict(from_attributes=True)


class AgentRunRequest(BaseModel):
    task: str
    model: str

    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        if v not in settings.SUPPORTED_LLM_MODELS:
            raise ValueError(f"Model '{v}' is not supported. Supported models: {settings.SUPPORTED_LLM_MODELS}")
        return v


class ToolCallLog(BaseModel):
    role: Literal["tool"] = "tool"
    name: str
    content: str
    status: Literal["success", "error"]
    attempt: int
    input: Optional[Any] = None


class AgentRunResponse(BaseModel):
    final_response: Optional[str]
    tool_calls: List[ToolCallLog] = Field(default_factory=list)
    prompt: str