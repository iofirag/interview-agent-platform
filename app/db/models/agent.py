from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    tenant = relationship("Tenant", back_populates="agents")
    tools = relationship("AgentTool", back_populates="agent", passive_deletes=True)
    executions = relationship("AgentExecution", back_populates="agent", passive_deletes=True)

    @property
    def tool_ids(self):
        return [at.tool_id for at in self.tools]
