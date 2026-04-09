from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.services import tool_service
from app.api.deps import get_db, get_tenant

router = APIRouter()

@router.post("/tools", response_model=schemas.Tool, tags=["Tools"], summary="Create a tool", description="Create a new tool for the tenant.")
def create_tool(tool: schemas.ToolCreate, db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    return tool_service.create_tool(db, tenant.id, tool.name, tool.description)

@router.get("/tools", response_model=List[schemas.Tool], tags=["Tools"], summary="List tools", description="List all tools for the tenant. Optionally filter by agent name.")
def list_tools(agent_name: Optional[str] = Query(None), db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    return tool_service.get_tools(db, tenant.id, agent_name)

@router.put("/tools/{tool_id}", response_model=schemas.Tool, tags=["Tools"], summary="Update a tool", description="Update an existing tool.")
def update_tool(tool_id: int, tool: schemas.ToolCreate, db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    updated = tool_service.update_tool(db, tenant.id, tool_id, tool.name, tool.description)
    if not updated:
        raise HTTPException(status_code=404, detail="Tool not found")
    return updated

@router.delete("/tools/{tool_id}", tags=["Tools"], summary="Delete a tool", description="Delete a tool by ID.")
def delete_tool(tool_id: int, db: Session = Depends(get_db), tenant=Depends(get_tenant)):
    deleted = tool_service.delete_tool(db, tenant.id, tool_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"ok": True}
