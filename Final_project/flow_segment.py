from hexifier import hexify
from settings import *


class FlowSegment(object):
    """
    Abstract flow segment object
    """

    def __init__(self, start_pos, end_pos):
        super(FlowSegment, self).__init__()
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.enabled = True
        self.table_section = None
        self.reset()

    def reset(self):
        self.direction = None
        self.state = State.PASSIVE if self.enabled else State.OFF
        self.voltage = Voltages.ERROR
        self.load = Load.NORMAL
        self.speed = Speed.NORMAL

    def set_force_disabled(self, enabled):
        self.enabled = enabled
        self.state = State.OFF if self.enabled is False else State.ACTIVE

    def activate(self):
        """
        Activates the flow if it is passive
        """
        if self.state is State.PASSIVE:
            self.state = State.ACTIVE

    def get_byte(self):
        """
        Get byte (hex string) with information about speed, direction, load and state
        """

        speed = self.speed << 5
        direction = (
                        self.direction if self.direction is not None else Direction.FORWARDS) << 4
        load = self.load << 2
        state = self.state
        byte = hexify(speed ^ direction ^ load ^ state)
        return [byte]

    def __repr__(self):
        return 'FlowSegment({0}, {1}) [s {2},v {3},l {4}]'.format(self.start_pos, self.end_pos, self.state,
                                                                  self.voltage, self.load)


class NeighborFlowSegment(FlowSegment):

    def __init__(self, start_pos, end_pos):
        super(NeighborFlowSegment, self).__init__(start_pos, end_pos)
