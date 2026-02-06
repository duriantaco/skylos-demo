# app/api/deps.py
from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings  # UNUSED (demo): not used
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # Super simple demo "auth"
    if x_api_key != "dev-key":
        raise HTTPException(status_code=401, detail="Invalid API key")

# UNUSED (demo): never used dependency
def get_actor_from_headers(x_actor: str | None = Header(default=None)) -> str:  # UNUSED (demo)
    return x_actor or "unknown"
