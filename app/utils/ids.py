# app/utils/ids.py
import uuid
import random
import string

def new_request_id() -> str:
    return uuid.uuid4().hex

# UNUSED (demo): unused function
def slugify(s: str) -> str:  # UNUSED (demo)
    return s.strip().lower().replace(" ", "-")

# UNUSED (demo): unused variable
DEFAULT_REQUEST_ID = "0000000000000000"  # UNUSED (demo)

def weak_token(n: int = 16) -> str:
    # INTENTIONALLY BAD (demo): predictable token generator
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(n))
