import os
from functools import lru_cache
from cryptography.fernet import Fernet

@lru_cache(maxsize=1)
def __get_fernet() -> Fernet:
    _key = os.environ.get("NOTION_ENCRYPT_SECRET")
    if _key is None:
        raise Exception("NOTION_ENCRYPT_SECRET couldn't be loaded")
    return Fernet(_key)

def custom_encrypt(text: str) -> str:
    return __get_fernet().encrypt(text.encode()).decode()


def custom_decrypt(token: str) -> str:
    return __get_fernet().decrypt(token.encode()).decode()
