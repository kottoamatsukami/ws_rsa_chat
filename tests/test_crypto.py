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
    crypto = utils.encode_message(message, pk)
    decoded = utils.decode_message(crypto, sk)
    assert decoded == message


def test_empty_message_decoding():
    message = "".encode('utf-8')
    (pk, sk) = rsa.newkeys(1024)
    crypto = utils.encode_message(message, pk)
    decoded = utils.decode_message(crypto, sk)
    assert decoded == message


def test_large_message_decoding():
    message = "kjdhkyasgyutu6f2tguywqtugk7c6f3yf42tfd67sdr67frwe6yfrtfsru61r37t462r6ytds86rtu623ey632r".encode('utf-8')
    (pk, sk) = rsa.newkeys(1024)
    crypto = utils.encode_message(message, pk)
    decoded = utils.decode_message(crypto, sk)
    assert decoded == message



