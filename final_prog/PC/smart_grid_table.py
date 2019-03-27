from settings import *
from logger import log
from table_section import *
from flow_segment import *
from module import *
from grid import Grid
import datetime

import json


class SmartGridTable(object):
    """
    SmartGridTable
    """

    def __init__(self, grid):
        super(SmartGridTable, self).__init__()
        self.table_sections = []
        self.modules = []
        self.load_modules()
        self.load_table_info()
        self.grid = grid
        self.last_recalculation_request_time = None

    def load_modules(self):
        self.modules = load_module_info()
        print self.modules

    def load_table_info(self):
        self.table_sections = load_table_info()

    def get_module(self, id):
        return next((module for module in self.modules if module.id == id), None)

    def get_modules(self):
        return self.modules

    def get_table_section(self, id):
        return next((tp for tp in self.get_table_sections() if tp.id == id), None)

    def get_table_sections(self):
        return [tp for tp in self.table_sections if tp.connected]

    def write_table_config(self):
        data = {
            "tableParts": []
        }
        for table_section in self.table_sections:
            data["tableParts"].append({
                "id": table_section.id,
                "type": table_section.type,
                "startPosition": table_section.pos
            })

        with open('config/tableConfig.json', 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

    def table_connected(self, table_id, location_id, payload):
        """
        A Table Section first connection to the main controller
        """
        table_section = next(
            (tp for tp in self.table_sections if tp.id == table_id), None)

        if not table_section.connected:
            log('New Table Section {0} connected'.format(table_id))
            table_section.connected = True

            # Add flow segments of table section to grid.
            for flow_segment in table_section.get_flows():
                self.grid.add_flow_segment(flow_segment)
        else:
            log('duplicate Table Section', table_section.id)
            table_section.clear_table()

    def module_config_changed(self, module_id, config_id, value):
        """
        Module configuration changed
        """
        module = self.get_module(module_id)
        if module is not None:
            module.save_configuration(config_id, value)
            if module.table_section is not None:
                self.last_recalculation_request_time = datetime.datetime.now()
                return True
        return False

    def module_placed(self, table_id, location_id, module_id):
        """
        A module is placed or removed from a Table Section
        """

        table_section = next(
            (tp for tp in self.get_table_sections() if tp.id == table_id), None)
        module = next((m for m in self.modules if m.id == module_id), None)

        if module is None and module_id is not 0:
            log('Unknown module id "{0}" using None instead'.format(module_id))

        # Place module on table section
        if table_section:
            unparsed_position = TABLE_PART[table_section.type][
                "module_locations"][location_id]["position"]
            position = (unparsed_position[
                        0] + table_section.pos[0], unparsed_position[1] + table_section.pos[1])
           
            log('Module {0} placed on tablesection {1}, location {2}, position {3}'.format(
                module, table_id, location_id, position))
            if module is not None:
                module.position = position
                module.set_table_section(table_section)

                if hasattr(module, 'linked_module') and module.linked_module.position is None:
                    # Get closest position to place a module
                    distance = 3
                    closest_position = None
                    closest_ts = None

                    for ts in self.table_sections:
                        if ts is table_section: continue
                        
                        for location in TABLE_PART[ts.type]["module_locations"]:
                            unparsed_position = location["position"]
                            module_position = (unparsed_position[0] + ts.pos[0], unparsed_position[1] + ts.pos[1])

                            if self.grid.get_module_on_position(module_position):
                                continue
                            
                            location_distance = self.grid.get_actual_distance_between_nodes(position, module_position)

                            if location_distance < distance:
                                distance = location_distance
                                closest_position = module_position
                                closest_ts = ts

                    if closest_position is None:
                        log('Tried to place a linked module, but there is no place to set the linked module less than ' + str(distance) + ' units away.')
                    else:
                        log('Added a linked module on position ' + str(closest_position))
                        module.linked_module.position = closest_position
                        module.linked_module.set_table_section(closest_ts)
            else:
                module = self.grid.get_module_on_position(position)

 
                if hasattr(module, 'linked_module') and module.linked_module.position is not None:
                    module.linked_module.position = None
                    module.linked_module.set_table_section(None)

                if hasattr(module, 'position'):
                    module.set_table_section(None)
                    module.position = None

            self.last_recalculation_request_time = datetime.datetime.now()
            return True
        return False

    def calculate(self):
        start = datetime.datetime.now()

        self.last_recalculation_request_time = None

        self.grid.reset()
        for table_section in self.get_table_sections():
            table_section.update()
        
        self.check_table_sections()
        self.grid.calculate()

        # Sync table section load and disabled state
        continue_loop = True
        while continue_loop:
            continue_loop = False
            for table_section in self.get_table_sections():
                result = table_section.update_after_calculation()
                if result is not False:
                    continue_loop = True

                    self.sync_attached_table_sections(table_section, result)

        # Sync table section speed
        continue_loop = True
        while continue_loop:
            continue_loop = False
            for table_section in self.get_table_sections():
                result = table_section.update_speed_after_calculation()
                if result:
                    continue_loop = True

                    self.sync_speed_of_attached_table_sections(table_section)

        self.grid.give_power_back_to_modules()

        end = datetime.datetime.now()
        delta = end - start

        log('* Finished calculating in ' + str(delta.total_seconds() * 1000) + 'ms.')
        
    def check_table_sections(self):
        log ('> Checking table sections for transformers and batteries')
        active_table_sections = []
        low_voltage_table_sections = []

        for table_section in self.table_sections:
            for module in table_section.modules:
                if not isinstance(module, TransformerModule) and not module.get_configuration(15):
                    continue

                # Check if any module can reach the transformer module
                should_be_active = True
                for other_module in table_section.modules:
                    if other_module is module:
                        continue
                    path = self.grid.astar(other_module.position, module.position)

                    if path is None:
                        should_be_active = False
                        continue
                    
                    should_be_active = True
                    break

                if should_be_active:
                    active_table_sections.append(table_section)

                break
            
            if table_section not in active_table_sections:
                table_section.disable()
                low_voltage_table_sections.append(table_section)

        # Enable attached table sections
        while len(active_table_sections):
            active_table_section = active_table_sections[0]
            active_table_section.enable()

            for flow_segment in active_table_section.flows:
                if not isinstance(flow_segment, NeighborFlowSegment):
                    continue
                
                affected_flow_segments = self.grid.find_flow_segments_on_position(flow_segment.start_pos) + self.grid.find_flow_segments_on_position(flow_segment.end_pos)

                for affected_flow_segment in affected_flow_segments:
                    if affected_flow_segment.table_section is flow_segment.table_section:
                        continue

                    log ("Trying to sync " + str(affected_flow_segment.table_section.id))
                    
                    synced = affected_flow_segment.table_section.enable()

                    if synced:
                        active_table_sections.append(affected_flow_segment.table_section)
                        log("<TS #" + str(affected_flow_segment.table_section.id) + "> has been reactivated as active <TS #" + str(active_table_section.id) + "> is attached to it")
            
            active_table_sections = active_table_sections[1:]
                    
        # Enable a low voltage table section if there is a battery module placed
        for table_section in low_voltage_table_sections:
            for module in table_section.modules:
                if module.voltage is not Voltages.ADAPTIVE:
                    continue
                
                log ("<TS #" + str(table_section.id) + "> has been re-enabled as there is a battery on it.")
                table_section.enable()
                break
        
        log('* Finished checking table sections.')


    def sync_speed_of_attached_table_sections(self, table_section):
        for flow in table_section.flows:
            if not isinstance(flow, NeighborFlowSegment):
                continue
            if not flow.enabled:
                continue

            affected_flow_segments = self.grid.find_flow_segments_on_position(
                flow.start_pos) + self.grid.find_flow_segments_on_position(flow.end_pos)

            for affected_flow_segment in affected_flow_segments:
                if not affected_flow_segment.enabled:
                    continue
                if affected_flow_segment.table_section is table_section:
                    continue

                if affected_flow_segment.table_section.get_speed() < table_section.get_speed():
                    affected_flow_segment.table_section.set_speed(
                        table_section.get_speed())
                    self.sync_speed_of_attached_table_sections(
                        affected_flow_segment.table_section)

    def sync_attached_table_sections(self, table_section, result):
        for flow in table_section.flows:
            if not isinstance(flow, NeighborFlowSegment):
                continue
            if not flow.enabled:
                continue

            affected_flow_segments = self.grid.find_flow_segments_on_position(
                flow.start_pos) + self.grid.find_flow_segments_on_position(flow.end_pos)

            for affected_flow_segment in affected_flow_segments:
                if not affected_flow_segment.enabled:
                    continue
                if affected_flow_segment.table_section is table_section:
                    continue

                affected_result = affected_flow_segment.table_section.sync_to_result(
                    result)
                log("Affecting " + str(table_section.id) +
                    " to result " + str(result))

                if affected_result:
                    self.sync_attached_table_sections(
                        affected_flow_segment.table_section, result)
                log("Affected result = " + str(affected_result))

    def get_flow_configurations(self):
        connected_table_sections = self.get_table_sections()
        flow_configs = []

        # Get config
        for table_section in connected_table_sections:
            flow_config_string = ''.join(table_section.get_flow_bytes())
            flow_configs.append({
                'destination': table_section.id,
                'config': flow_config_string
            })

        return flow_configs
