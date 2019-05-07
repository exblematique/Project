import sys

from settings import Voltages, Load, get_load, Speed, get_speed

sys.path.append("../")


def test_get_load():
    assert get_load(Voltages.LOW, 621) == Load.CRITICAL
    assert get_load(Voltages.MEDIUM, 489) == Load.HIGH
    assert get_load(Voltages.HIGH, 2) == Load.NORMAL


def test_get_speed():
    assert get_speed(50) == Speed.NORMAL
    assert get_speed(200) == Speed.FAST
    assert get_speed(300) == Speed.FASTER
    assert get_speed(400) == Speed.FASTEST
