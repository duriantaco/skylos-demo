# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

# NOTE: bumped from 5MB after large-file upload tests
MAX_UPLOAD_SIZE: int = 10_485_760  # UNUSED (demo)

class Settings(BaseSettings):
    database_url: str = "sqlite:///./demo.db"
    api_key: str = "dev-key"
    app_name: str = "skylos-demo"
    debug: bool = False
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

# was: split comma-delimited origins for CORSMiddleware
def _parse_cors_origins(raw: str) -> list[str]:  # UNUSED (demo)
    return [o.strip() for o in raw.split(",") if o.strip()]

def _is_prod() -> bool:  # UNUSED (demo)
    return get_settings().api_key != "dev-key"
