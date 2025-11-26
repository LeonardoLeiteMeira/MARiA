import os
from functools import lru_cache
from cryptography.fernet import Fernet

_SECRET_KEY_ENV = "APP_SECRET_KEY"

@lru_cache(maxsize=1)
def __get_fernet() -> Fernet:
    _key = os.environ.get(_SECRET_KEY_ENV)
    if _key is None:
        raise Exception("APP_SECRET_KEY couldn't be loaded")
    return Fernet(_key)

def custom_encrypt(text: str) -> str:
    return __get_fernet().encrypt(text.encode()).decode()


def custom_decrypt(token: str) -> str:
    return __get_fernet().decrypt(token.encode()).decode()
