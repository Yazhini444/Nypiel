import bcrypt
import hashlib
import hmac


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False

    # Check for standard bcrypt hash ($2a$, $2b$, $2y$)
    if hashed.startswith(("$2a$", "$2b$", "$2y$")):
        password_bytes = plain.encode("utf-8")[:72]
        try:
            return bcrypt.checkpw(password_bytes, hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False

    # Check for legacy 64-character SHA-256 hex hash
    if len(hashed) == 64 and all(c in "0123456789abcdefABCDEF" for c in hashed):
        computed = hashlib.sha256(plain.encode("utf-8")).hexdigest()
        return hmac.compare_digest(computed.lower(), hashed.lower())

    return False