import hashlib
import hmac
import secrets

ROLE_ADMIN = "admin"
ROLE_VIEWER = "viewer"  # UNUSED (demo)
TOKEN_ALGORITHM = "HS256"  # UNUSED (demo)

_API_KEY_SALT = "skylos-demo-salt"


def hash_api_key(key: str) -> str:
    return hashlib.sha256((_API_KEY_SALT + key).encode()).hexdigest()


def verify_api_key(key: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_api_key(key), hashed)


def validate_bearer_token(token: str) -> dict:  # UNUSED (demo)
    # TODO: replace stub with real JWT decode using TOKEN_ALGORITHM
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")
    return {"sub": "demo-user", "role": ROLE_ADMIN}


def generate_api_token(user_id: str, role: str = ROLE_ADMIN) -> str:  # UNUSED (demo)
    raw = f"{user_id}:{role}:{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()


def check_ip_allowlist(ip: str, allowlist: list[str] | None = None) -> bool:  # UNUSED (demo)
    if allowlist is None:
        return True
    return ip in allowlist
