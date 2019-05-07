import sys

import pytest
from helper_fns import INVALID_VALUE

from settings import Voltages, COLOR_DICT

sys.path.append("../")


def test_enum_to_color():
    fn = Voltages.enum_to_color
    assert fn(Voltages.ERROR) == (1.0, 0.0, 0.0, 1.0)
    assert fn(Voltages.LOW) == COLOR_DICT["vlow"]["color"]
    assert fn(Voltages.MEDIUM) == COLOR_DICT["vmedium"]["color"]
    assert fn(Voltages.HIGH) == COLOR_DICT["vhigh"]["color"]
    with pytest.raises(Exception):
        fn(INVALID_VALUE)


def test_enum_to_flow_color():
    fn = Voltages.enum_to_flow_color
    assert fn(Voltages.ERROR) == (1, 1, 1, 1)
    assert fn(Voltages.LOW) == COLOR_DICT["vlow"]["color"]
    assert fn(Voltages.MEDIUM) == COLOR_DICT["vmedium"]["color"]
    assert fn(Voltages.HIGH) == COLOR_DICT["vhigh"]["color"]
    with pytest.raises(Exception):
        fn(INVALID_VALUE)


def test_str_to_enum():
    fn = Voltages.str_to_enum
    assert fn("error") == Voltages.ERROR
    assert fn("low") == Voltages.LOW
    assert fn("medium") == Voltages.MEDIUM
    assert fn("high") == Voltages.HIGH
    with pytest.raises(Exception):
        fn(INVALID_VALUE)


def test_enum_to_str():
    fn = Voltages.enum_to_str
    assert fn(Voltages.ERROR) == "Error"
    assert fn(Voltages.LOW) == "Low"
    assert fn(Voltages.MEDIUM) == "Medium"
    assert fn(Voltages.HIGH) == "High"
    with pytest.raises(Exception):
        fn(INVALID_VALUE)
