# ADD PARENT DIR
import sys
from pathlib import Path

project_root = Path(__file__).absolute()
sys.path.append(project_root.parent.parent.__str__())
#

from core import utils
import rsa


def test_normal_message_decoding():
    message = "Hello, from user A".encode('utf-8')
    (pk, sk) = rsa.newkeys(1024)
    status, crypto = utils.encode_message(message, pk)
    assert status is True
    status, decoded = utils.decode_message(crypto, sk)
    assert status is True
    assert decoded == message


def test_empty_message_decoding():
    message = "".encode('utf-8')
    (pk, sk) = rsa.newkeys(1024)
    status, crypto = utils.encode_message(message, pk)
    assert status is True
    status, decoded = utils.decode_message(crypto, sk)
    assert status is True
    assert decoded == message


def test_large_message_decoding():
    message = "kjdhkyasgyutu6f2tguywqtugk7c6f3yf42tfd67sdr67frwe6yfrtfsru61r37t462r6ytds86rtu623ey632r".encode('utf-8')
    (pk, sk) = rsa.newkeys(1024)
    status, crypto = utils.encode_message(message, pk)
    assert status is True
    status, decoded = utils.decode_message(crypto, sk)
    assert status is True
    assert decoded == message


def test_should_raise_error():
    message = "test".encode('utf-8')
    (a_pk, a_sk) = rsa.newkeys(1024)
    (b_pk, b_sk) = rsa.newkeys(1024)
    status, crypto = utils.encode_message(message, a_pk)
    assert status is True
    status, decoded = utils.decode_message(crypto, b_sk)
    assert status is False
