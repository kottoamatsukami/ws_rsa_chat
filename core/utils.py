from rsa import PublicKey, PrivateKey, encrypt, decrypt
from ast import literal_eval
from datetime import datetime


def encode_message(message_utf: bytes, pub_key: PublicKey) -> bytes:
    encoded_message = encrypt(message_utf, pub_key)
    return encoded_message


def decode_message(encoded_message: bytes, priv_key: PrivateKey) -> bytes:
    decoded_message = decrypt(encoded_message, priv_key)
    return decoded_message


def extract_bytes_from_str(s: str) -> tuple[bool, bytes]:
    try:
        s = literal_eval(s)
        return True, s

    except ValueError:
        return False, s


def lazy_logger_factory(type_of_logging: str):
    return lambda message: print(f"[{datetime.now()}][{type_of_logging}]: {message}")


info     = lazy_logger_factory("info")
debug    = lazy_logger_factory("debug")
warning  = lazy_logger_factory("warning")
error    = lazy_logger_factory("error")
critical = lazy_logger_factory("critical")


__all__ = [
    'encode_message',
    'decode_message',
    'extract_bytes_from_str',

    'info',
    'debug',
    'warning',
    'error',
    'critical'
]