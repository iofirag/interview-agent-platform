from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services import health_service
from app.api.deps import get_db

router = APIRouter()

@router.get("/ping", tags=["Health"], summary="Health check", description="Check API status.")
def ping(db: Session = Depends(get_db)):
    try:
        return health_service.ping(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
