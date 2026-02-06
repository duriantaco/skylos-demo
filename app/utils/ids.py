# app/utils/ids.py
import uuid

def new_request_id() -> str:
    return uuid.uuid4().hex

# UNUSED (demo): unused function
def slugify(s: str) -> str:  # UNUSED (demo)
    return s.strip().lower().replace(" ", "-")

# UNUSED (demo): unused variable
DEFAULT_REQUEST_ID = "0000000000000000"  # UNUSED (demo)
