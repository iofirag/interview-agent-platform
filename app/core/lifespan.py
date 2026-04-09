from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.base import Base
from app.db.repositories import tenant_repo
from app.db.session import engine
from app.db.session import engine, SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Seed data
    with SessionLocal() as db:
        tenant_repo.seed_hardcoded_tenants(db)
    yield