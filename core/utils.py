from rsa import PublicKey, PrivateKey, encrypt, decrypt
from ast import literal_eval
from datetime import datetime


def encode_message(message_utf: bytes, pub_key: PublicKey) -> tuple[bool, bytes]:
    """
    This function encode message with pub_key
    :param message_utf:
    :param pub_key:
    :return: status and message bytes representation
    """
    try:
        encoded_message = encrypt(message_utf, pub_key)
        return True, encoded_message
    except OverflowError:
        return False, message_utf


def decode_message(encoded_message: bytes, priv_key: PrivateKey) -> tuple[bool, bytes]:
    """
    This function decode message with priv_key
    :param encoded_message:
    :param priv_key:
    :return: status and message bytes representation
    """
    try:
        decoded_message = decrypt(encoded_message, priv_key)
        return True, decoded_message
    except ValueError:
        return False, encoded_message


def extract_bytes_from_str(s: str) -> tuple[bool, bytes]:
    """
    This function extracts bytes from a string
    :param s:
    :return: status and message bytes representation
    """
    try:
        s = literal_eval(s)
        return True, s

    except ValueError:
        return False, s


def lazy_logger_factory(type_of_logging: str):
    """
    This is lazy logging implement
    :param type_of_logging:
    :return:
    """
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