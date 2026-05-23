import base64

def mask_api_key(raw: str) -> str:
    if not raw:
        return ""
    if len(raw) <= 8:
        return raw[:2] + "****"
    return f"{raw[:2]}****{raw[-4:]}"


def encrypt_api_key(raw: str) -> str:
    return base64.b64encode(raw.encode("utf-8")).decode("utf-8") if raw else ""


def decrypt_api_key(encoded: str) -> str:
    return base64.b64decode(encoded.encode("utf-8")).decode("utf-8") if encoded else ""
