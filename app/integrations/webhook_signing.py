from __future__ import annotations

import hmac
import hashlib
from typing import Optional


def _safe_str_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def sign_hmac_sha256(secret: str, body: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256)
    return mac.hexdigest()


def verify_hmac_sha256(
    *,
    secret: str,
    body: bytes,
    signature: Optional[str],
) -> bool:
    if not signature:
        return False
    expected = sign_hmac_sha256(secret, body)
    return _safe_str_eq(expected, signature)


# DEAD (currently unused): alternative signature format, not referenced anywhere
def verify_hmac_sha256_prefixed(
    *,
    secret: str,
    body: bytes,
    signature: Optional[str],
    prefix: str = "sha256=",
) -> bool:
    if not signature or not signature.startswith(prefix):
        return False
    return verify_hmac_sha256(secret=secret, body=body, signature=signature[len(prefix) :])
