import sys

from dummySerial import DummySerial

sys.path.append("./dummy")


def test_valid_serial():
    assert DummySerial.name[:8] == '/dev/pts'
