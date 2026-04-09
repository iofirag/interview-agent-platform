from sqlalchemy.orm import Session
from sqlalchemy import text

def ping(db: Session):
    # Execute a minimal query to verify connection
    db.execute(text("SELECT 1"))
    return {"status": "ok", "message": "Database is reachable"}
