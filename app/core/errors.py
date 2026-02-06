# app/core/errors.py
from fastapi import HTTPException

def not_found(entity: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{entity} not found")

# UNUSED (demo): not used anywhere
class DemoError(Exception):  # UNUSED (demo)
    pass
