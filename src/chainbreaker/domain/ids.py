from hashlib import sha256


def stable_id(prefix: str, *parts: object) -> str:
    payload = "|".join(str(part) for part in parts).encode()
    return f"{prefix}-{sha256(payload).hexdigest()[:12]}"
