# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.db.models import Base

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

# UNUSED (demo): not used
def _drop_all() -> None:  # UNUSED (demo)
    Base.metadata.drop_all(bind=engine)
