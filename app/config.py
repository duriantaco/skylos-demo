# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./demo.db"
    api_key: str = "dev-key"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

# UNUSED (demo): never called
def _is_prod() -> bool:  # UNUSED (demo)
    return get_settings().api_key != "dev-key"