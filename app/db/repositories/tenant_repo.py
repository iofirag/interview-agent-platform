from sqlalchemy.orm import Session
from app.db.models import Tenant
from app.core.config import settings

def seed_hardcoded_tenants(db: Session):
    """
    Ensure all HARDCODED_TENANTS exist in the database.
    """
    for api_key, tenant in settings.HARDCODED_TENANTS.items():
        existing = db.query(Tenant).filter((Tenant.id == tenant["id"]) | (Tenant.api_key == api_key)).first()
        if not existing:
            db.add(Tenant(id=tenant["id"], name=tenant["name"], api_key=api_key))
    db.commit()

def get_tenant_by_api_key(db: Session, api_key: str):
    return db.query(Tenant).filter(Tenant.api_key == api_key).first()
