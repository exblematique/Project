from file_writer import read_contents_from_file
from flow_segment import *
from logger import log
from module import Module, DefaultModule


def load_table_info():
    """
    Load tables from the config/tableConfig.json file.
    """
    table_sections = []

    data = read_contents_from_file(TABLE_CONFIG_FILE)
    for table_info in data.get("tableParts"):
        table_sections.append(TableSection(
            int(table_info.get("id")),
            int(table_info.get("type")),
            tuple(table_info.get("startPosition")),
            table_info.get("neighbours")))

    return table_sections


class TableSection(object):
    """
    Table Section object, contains flow structure
    """

    def __init__(self, id, table_type, start_pos, neighbours):
        super(TableSection, self).__init__()
        """
        Init Table Section, set id, table type and flows based on table type
        """

        # Set fields
        self.id = id
        self.type = table_type
        self.voltage = Voltages.ERROR
        self.connected = False
        self.modules = []
        self.pos = (0, 0)
        self.neighbours = neighbours
        self.fake_disabled = False  # This is being used for fake syncing table sections to surrounding table sections (for battery)

        # Set flows
        if table_type == 1:  # final table design
            self.flows = [
                FlowSegment((0, 2), (1, 2)),
                FlowSegment((1, 2), (1, 1)),
                FlowSegment((1, 1), (2, 1)),
                NeighborFlowSegment((2, 1), (2, 0)),
                FlowSegment((2, 1), (3, 1)),
                FlowSegment((3, 1), (3, 2)),
                FlowSegment((3, 2), (4, 2)),
                FlowSegment((3, 2), (3, 3)),
                FlowSegment((3, 3), (2, 3)),
                NeighborFlowSegment((2, 3), (2, 4)),
                FlowSegment((2, 3), (1, 3)),
                FlowSegment((1, 3), (1, 2))
            ]
        elif table_type == 2:
            self.flows = [
                FlowSegment((0, 4), (1, 4)),
                FlowSegment((1, 4), (1, 3)),
                FlowSegment((1, 3), (1, 2)),
                FlowSegment((1, 2), (2, 2)),
                FlowSegment((2, 2), (3, 2)),
                FlowSegment((3, 2), (2, 2)),
                FlowSegment((2, 2), (1, 2)),
                FlowSegment((1, 2), (0, 2)),
                FlowSegment((1, 2), (1, 1)),
                FlowSegment((1, 1), (1, 0)),
                FlowSegment((1, 0), (0, 0))
            ]

        else:  # Unknown table type
            self.type = 1
            log('Unknown table type initiated', table_type)
            self.flows = []

        for flow in self.flows:
            flow.table_section = self

        # Set position of flow segments relative to starting position of
        # table section
        self.set_position(start_pos)

    def add_module(self, module):
        self.modules.append(module)

    def remove_module(self, module):
        self.modules.remove(module)

    def set_position(self, position):
        if position is None:
            self.pos = None
            return

        position_increase = (position[
                                 0] - self.pos[0], position[1] - self.pos[1]) if self.pos is not None else position
        self.pos = position
        for flow_segment in self.flows:
            flow_segment.start_pos = (flow_segment.start_pos[
                                          0] + position_increase[0], flow_segment.start_pos[1] + position_increase[1])
            flow_segment.end_pos = (flow_segment.end_pos[
                                        0] + position_increase[0], flow_segment.end_pos[1] + position_increase[1])

        for module in self.get_placed_modules():
            if hasattr(module, 'position') and module.position is not None:
                module.position = (module.position[
                                       0] + position_increase[0], module.position[1] + position_increase[1])

    def get_placed_modules(self, module_type=None):
        """
        Returns placed modules based on given module type, default on all modules
        """
        module_type = module_type if module_type else Module
        return [module for module in self.modules if isinstance(module, module_type)]

    def get_flows(self, flow_type=None):
        """
        Returns flows based on given flow type, default on all flows
        """
        flow_type = flow_type if flow_type else FlowSegment
        return [f for f in self.flows if isinstance(f, flow_type)]

    def get_voltage(self, string=False):
        return Voltages.enum_to_str(self.voltage) if string else self.voltage

    def clear_table(self):
        """
        Remove all modules and neighbors from the table
        """
        for module in self.get_placed_modules():
            module.set_table_section(None)

    def get_remaining_power(self):
        """
        Get power of this table section and all sections behind it
        """
        power = 0
        for module in self.get_placed_modules(DefaultModule):
            power = power + module.remaining_power

        return power

    def update(self):
        preferred_voltage = {}
        for module in self.get_placed_modules():
            if module.voltage is None or module.voltage is Voltages.ADAPTIVE:
                continue

            if module.voltage not in preferred_voltage:
                preferred_voltage[module.voltage] = 0

            preferred_voltage[module.voltage] += 1

        if len(preferred_voltage) > 0:
            self.voltage = max(preferred_voltage, key=preferred_voltage.get)
        else:
            for f in self.flows:
                f.state = State.OFF

        self.fake_disabled = False

    def update_after_calculation(self):
        """
        Returns:
            False if the table section is already disabled.
            True if the whole table section gets disabled.
            Load.CRITICAL if the flow segments get set to Load.CRITICAL
            Load.HIGH if the flow segments get set to Load.HIGH
        """
        prefer_load = None
        if not self.is_enabled():
            return False

        # Flash critical when there is not enough power
        remaining_power = self.get_remaining_power()
        if remaining_power < -200:
            return self.disable()

        for flow_segment in self.flows:
            if -200 < remaining_power < -100 and flow_segment.direction is not None:
                prefer_load = Load.CRITICAL
            if -100 <= remaining_power < 0 and flow_segment.direction is not None:
                prefer_load = Load.HIGH

        log("Remaining power of <TS #" + str(self.id) + "> = " + str(self.get_remaining_power()))

        # Disable flow segments if no power is flowing
        should_disable = True
        for flow_segment in self.flows:
            if flow_segment.direction is not None:
                should_disable = False
                break

        if should_disable:
            return self.disable()

        if prefer_load is not None and not self.is_synced_to_result(prefer_load):
            self.sync_to_result(prefer_load)
            return prefer_load

        return False

    def sync_to_result(self, result):
        if not self.is_enabled():
            return False

        if self.is_synced_to_result(result):
            return False

        if result is True:
            if self.is_battery_placed_on_table_section():
                if self.fake_disabled:
                    return False

                self.fake_disabled = True
                return True

            return self.disable()

        for flow_segment in self.flows:
            if result is Load.CRITICAL:
                flow_segment.load = Load.CRITICAL

            if result is Load.HIGH:
                flow_segment.load = Load.HIGH

        return False

    def is_synced_to_result(self, result):
        is_synced = True
        if result is True:
            return not self.is_enabled()

        if result is Load.CRITICAL:
            for flow_segment in self.flows:
                if flow_segment.direction is not None and flow_segment.load is not Load.CRITICAL:
                    is_synced = False
                    break

        elif result is Load.HIGH:
            for flow_segment in self.flows:
                if flow_segment.direction is not None and flow_segment.load is not Load.HIGH and flow_segment.load is not Load.CRITICAL:
                    is_synced = False
                    break

        return is_synced

    def disable(self):
        if not self.is_enabled():
            return False

        self.voltage = Voltages.ERROR

        for flow_segment in self.flows:
            flow_segment.reset()
            flow_segment.state = State.OFF

        log("<TS #" + str(self.id) + "> disabled")

        return True

    def is_battery_placed_on_table_section(self):
        for module in self.get_placed_modules():
            if module.voltage is Voltages.ADAPTIVE:
                return True

        return False

    def enable(self):
        if self.is_enabled():
            return False

        for flow_segment in self.flows:
            flow_segment.reset()

        self.update()
        return True

    def is_enabled(self):
        any_segment_active = False
        for flow_segment in self.flows:
            if flow_segment.state is not State.OFF:
                any_segment_active = True
                break

        return any_segment_active

    def update_speed_after_calculation(self):
        desired_speed = max(Speed.NORMAL, get_speed(
            self.get_remaining_power()), self.get_speed())

        if desired_speed is not self.get_speed():
            self.set_speed(desired_speed)
            return True

        return False

    def get_speed(self):
        speed = Speed.NORMAL
        for flow_segment in self.flows:
            if flow_segment.speed > speed:
                speed = flow_segment.speed

        return speed

    def set_speed(self, speed):
        for flow_segment in self.flows:
            flow_segment.speed = speed

    def activate(self):
        for f in self.flows:
            f.activate()

    def get_header_byte(self):
        voltage = self.voltage if self.voltage is not Voltages.ERROR else 0
        voltage = voltage << 6
        byte = hexify(voltage)
        return [byte]

    def get_flow_bytes(self):
        # Get header byte and byte array
        header_byte = self.get_header_byte()
        flow_byte_array = []
        for f in self.flows:
            flow_byte_array = flow_byte_array + f.get_byte()
        return header_byte + flow_byte_array

    def __repr__(self):
        return 'table section {0}, {1} voltage'.format(self.id, self.get_voltage(True))
