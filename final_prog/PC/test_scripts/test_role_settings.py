import sys

import pytest
from helper_fns import INVALID_VALUE

from settings import Roles

sys.path.append("../")


def test_str_to_enum():
    fn = Roles.str_to_enum
    assert fn("production") == Roles.PRODUCTION
    assert fn("consumption") == Roles.CONSUMPTION
    with pytest.raises(Exception):
        fn(INVALID_VALUE)


def test_enum_to_str():
    fn = Roles.enum_to_str
    assert fn(Roles.PRODUCTION) == "production"
    assert fn(Roles.CONSUMPTION) == "consumption"
    with pytest.raises(Exception):
        fn(INVALID_VALUE)
