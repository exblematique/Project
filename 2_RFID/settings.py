"""
Debugging
"""

DEBUG = True

"""
Time configuration in seconds
"""
CONFIG_SEND_DELAY = 0.2

SYNC_DELAY = 20

"""
Module configuration file location
"""
MODULE_CONFIG_FILE = 'config/moduleConfig.json'
TABLE_CONFIG_FILE = 'config/tableConfig.json'

"""
Colors used in application
"""
COLOR_DICT = {
    "vlow": {
        "id": 0,
        "color": (0.1, 0.8, 1.0, 1.0)  # white-ish
    },
    "vmedium": {
        "id": 1,
        "color": (0.6, 0.3, 1.0, 1.0)  # light purple
    },
    "vhigh": {
        "id": 2,
        "color": (0.2, 0.1, 1.0, 1.0)  # Dark blue
    },
    "lnormal": {
        "id": 3,
        "color": (0, 1, 0, 1),  # Green
    },
    "lhigh": {
        "id": 4,
        "color": (1, 1, 0, 1),  # Yellow
    },
    "lstressed": {
        "id": 5,
        "color": (1, 0, 0, 1)   # Red
    }
}

"""
Enums
"""

# Grid voltages


class Voltages:
    ERROR, LOW, MEDIUM, HIGH, ADAPTIVE = range(-1, 4)

    @staticmethod
    def enum_to_color(e):
        if e is Voltages.ERROR:
            return (1.0, .0, .0, 1.0)
        elif e is Voltages.LOW:
            return COLOR_DICT["vlow"]["color"]
        elif e is Voltages.MEDIUM:
            return COLOR_DICT["vmedium"]["color"]
        elif e is Voltages.HIGH:
            return COLOR_DICT["vhigh"]["color"]
        raise Exception('Cannot convert this to color')

    @staticmethod
    def enum_to_flow_color(e):
        if e is Voltages.ERROR:
            return (1, 1, 1, 1)
        elif e is Voltages.LOW:
            return COLOR_DICT["vlow"]["color"]
        elif e is Voltages.MEDIUM:
            return COLOR_DICT["vmedium"]["color"]
        elif e is Voltages.HIGH:
            return COLOR_DICT["vhigh"]["color"]
        raise Exception('Cannot convert this to color')

    @staticmethod
    def str_to_enum(s):
        if s == "error":
            return Voltages.ERROR
        elif s == "low":
            return Voltages.LOW
        elif s == "medium":
            return Voltages.MEDIUM
        elif s == "high":
            return Voltages.HIGH
        elif s == None:
            return Voltages.ADAPTIVE
        raise Exception('Cannot convert this to enum')

    @staticmethod
    def enum_to_str(e):
        if e is Voltages.ERROR:
            return "Error"
        elif e is Voltages.LOW:
            return "Low"
        elif e is Voltages.MEDIUM:
            return "Medium"
        elif e is Voltages.HIGH:
            return "High"
        elif e is Voltages.ADAPTIVE:
            return "Adaptive"
        raise Exception('Cannot convert this to string')


class Roles:
    PRODUCTION, CONSUMPTION = range(2)

    @staticmethod
    def str_to_enum(s):
        if s == "production":
            return Roles.PRODUCTION
        elif s == "consumption":
            return Roles.CONSUMPTION
        raise Exception('Cannot convert this to enum')

    @staticmethod
    def enum_to_str(e):
        if e == Roles.PRODUCTION:
            return "production"
        elif e == Roles.CONSUMPTION:
            return "consumption"
        raise Exception('Cannot convert this to enum')


# FlowSegment speed
class Speed:
    NORMAL, FAST, FASTER, FASTEST = range(4)

# FlowSegment direction


class Direction:
    FORWARDS, BACKWARDS = range(2)

# FlowSegment load


class Load:
    NORMAL, HIGH, CRITICAL = range(3)

# FlowSegment state


class State:
    OFF, ERROR, PASSIVE, ACTIVE = range(4)


"""
Boundaries
"""
POWER_SPEED_BOUNDARIES = {
    Speed.NORMAL: 50,
    Speed.FAST: 200,
    Speed.FASTER: 300
}

VOLTAGE_POWER_LOAD_BOUNDARIES = {
    Voltages.LOW: {
        Load.CRITICAL: 300,     # capacity, power > capacity -> critical load
        Load.HIGH: .75          # high modifier, power > capacity * high modifier -> high load
    },
    Voltages.MEDIUM: {
        Load.CRITICAL: 500,     # capacity, critical load
        Load.HIGH: .80          # x% of capacity, high load
    },
    Voltages.HIGH: {
        Load.CRITICAL: 1300,     # capacity, critical load
        Load.HIGH: .90          # x% of capacity, high load
    }
}

"""
Helper functions
"""


def GET_LOAD(voltage, power):
    power = abs(power)
    high_mod = VOLTAGE_POWER_LOAD_BOUNDARIES[voltage][Load.HIGH]
    capacity = VOLTAGE_POWER_LOAD_BOUNDARIES[voltage][Load.CRITICAL]
    if power <= high_mod * capacity:
        return Load.NORMAL
    elif power <= capacity:
        return Load.HIGH
    else:
        return Load.CRITICAL


def GET_SPEED(power):
    if power <= POWER_SPEED_BOUNDARIES[Speed.NORMAL]:
        return Speed.NORMAL
    elif power <= POWER_SPEED_BOUNDARIES[Speed.FAST]:
        return Speed.FAST
    elif power <= POWER_SPEED_BOUNDARIES[Speed.FASTER]:
        return Speed.FASTER
    else:
        return Speed.FASTEST


"""
Table Section settings, per type.
example: x in TABLE_PART[type]['module_locations']
"""
TABLE_PART = {
    1: {
        'module_locations': [
            {
                'position': (0, 2)
            },
            {
                'position': (1, 1)
            },
            {
                'position': (3, 1)
            },
            {
                'position': (4, 2)
            },
            {
                'position': (3, 3)
            },
            {
                'position': (1, 3)
            }
        ],
    },
    2: {
        'module_locations': [
            {
                'position': (0, 2)
            },
            {
                'position': (0, 0)
            },
            {
                'position': (-1, -1)
            },
            {
                'position': (3, 2)
            },
            {
                'position': (-1, -1)
            },
            {
                'position': (0, 4)
            }
        ]
    }
}
