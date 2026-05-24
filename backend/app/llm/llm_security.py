import base64
import os
from cryptography.fernet import Fernet


def mask_api_key(raw: str) -> str:
    if not raw:
        return ""
    return "****" + raw[-4:]


def _fernet() -> Fernet:
    mk = os.getenv("LLM_CREDENTIAL_MASTER_KEY", "")
    if not mk:
        raise ValueError("LLM_CREDENTIAL_MASTER_KEY 未配置")
    key = mk.encode("utf-8")
    if len(mk) != 44:
        key = base64.urlsafe_b64encode(mk.encode("utf-8").ljust(32, b"0")[:32])
    return Fernet(key)


def encrypt_api_key(raw: str) -> str:
    if not raw:
        return ""
    return _fernet().encrypt(raw.encode("utf-8")).decode("utf-8")


def decrypt_api_key(cipher: str) -> str:
    if not cipher:
        return ""
    return _fernet().decrypt(cipher.encode("utf-8")).decode("utf-8")
