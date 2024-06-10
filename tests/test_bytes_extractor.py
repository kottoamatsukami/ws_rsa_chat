# ADD PARENT DIR
import sys
from pathlib import Path
project_root = Path(__file__).absolute()
sys.path.append(project_root.parent.parent.__str__())
#

from core import utils


def test_normal_case():
    string = 'Hello, World!'
    bytes_ = string.encode('utf-8')
    str_of_bytes = str(bytes_)
    status, result = utils.extract_bytes_from_str(str_of_bytes)
    assert status is True
    assert result == bytes_


def test_empty_case():
    string = ''
    bytes_ = string.encode('utf-8')
    str_of_bytes = str(bytes_)
    status, result = utils.extract_bytes_from_str(str_of_bytes)
    assert status is True
    assert result == bytes_


def test_large_case():
    string = 'ldjfkgjdhubh37itygys7f7iyt29hudgsyitft28eury2h78bchc7ayo27t4g1gu2ytgf78stgdq4t2fyufrydas76'
    bytes_ = string.encode('utf-8')
    str_of_bytes = str(bytes_)
    status, result = utils.extract_bytes_from_str(str_of_bytes)
    assert status is True
    assert result == bytes_


def test_should_raise_error():
    string = 'print("Exploit")'
    bytes_ = string
    str_of_bytes = str(bytes_)
    status, result = utils.extract_bytes_from_str(str_of_bytes)
    print(status, result)
    assert status is False