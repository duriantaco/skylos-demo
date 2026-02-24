# app/db/session.py
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.db.models import Base

settings = get_settings()

DB_POOL_SIZE: int = 10  # UNUSED (demo)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_engine_info() -> dict:  # UNUSED (demo)
    inspector = inspect(engine)
    return {
        "dialect": engine.dialect.name,
        "tables": inspector.get_table_names(),
    }

def _drop_all() -> None:  # UNUSED (demo)
    Base.metadata.drop_all(bind=engine)

def _reset_sequences(db_session) -> None:  # UNUSED (demo)
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
