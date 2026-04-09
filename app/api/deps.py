from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.repositories import tenant_repo as tenant

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tenant(api_key: str = Header(..., alias="x-api-key"), db: Session = Depends(get_db)):
    tenant_obj = tenant.get_tenant_by_api_key(db, api_key)
    if not tenant_obj:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return tenant_obj
