import os

from cryptography.fernet import Fernet

_SECRET_KEY_ENV = "APP_SECRET_KEY"

_key = os.environ.get(_SECRET_KEY_ENV)
if _key is None:
    _key = Fernet.generate_key()
    print(f"Secret key not found in environment; generated new key for runtime.")

_f = Fernet(_key)


def custom_encrypt(text: str) -> str:
    return _f.encrypt(text.encode()).decode()


def custom_decrypt(token: str) -> str:
    return _f.decrypt(token.encode()).decode()
