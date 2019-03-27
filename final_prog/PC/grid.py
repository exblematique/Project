from astar import AStar
import math
import datetime
from settings import Direction, State, Speed, Load, GET_SPEED, GET_LOAD, Voltages
from module import DefaultModule, TransformerModule
from logger import log
from flow import Flow

class Grid(AStar, object):
    """
    A class to define a network of flow segments and modules for distributing power,
    which allows pathfinding to happen between modules using the A* search algorithm.
    """

    def __init__(self, smart_grid_app):
        super(Grid, self).__init__()
        self.flow_segments = []
        self.exclude_match_list = []
        self.flows = []
        self.smart_grid_app = smart_grid_app

    def distance_between(self, n1, n2):
        """
        Get the distance between two vertices, using heuristic_cost_estimate
        """
        return self.heuristic_cost_estimate(n1, n2)

    def get_total_path_distance(self, path):
        """
        Get total distance in units of a path
        """
        distance = 0

        for i, node in enumerate(path):
            if i > len(path) - 2:
                break

            next_node = path[i + 1]
            distance += self.distance_between(node, next_node)

        return distance

    def heuristic_cost_estimate(self, node_1, node_2):
        """
        Calculate the distance between two vertices
        """
        return 1

    def get_actual_distance_between_nodes(self, node_1, node_2):
        """
        Calculate the distance between two vertices
        """
        (x1, y1) = node_1
        (x2, y2) = node_2
        return math.hypot(x2 - x1, y2 - y1)

    def neighbors(self, node):
        """
        Retrieve the connected vertice(s) of a given vertice
        """
        nodes = []
        for flow_segment in self.flow_segments:
            # Only add a neighbor if the flow segment direction allows it to
            if flow_segment.enabled is False or flow_segment.state is State.ERROR or flow_segment.state is State.OFF:
                continue

            is_start_pos_equal = flow_segment.start_pos[0] is node[
                0] and flow_segment.start_pos[1] is node[1]
            is_end_pos_equal = flow_segment.end_pos[0] is node[
                0] and flow_segment.end_pos[1] is node[1]

            if (flow_segment.direction is None or flow_segment.direction is
                    Direction.FORWARDS) and is_start_pos_equal:
                nodes.append(flow_segment.end_pos)
            elif (flow_segment.direction is None or flow_segment.direction is
                  Direction.BACKWARDS) and is_end_pos_equal:
                nodes.append(flow_segment.start_pos)

        # Add transformer locations
        for module in self.get_modules():
            if not isinstance(module, TransformerModule):
                continue

            pos = node
            module_pos = module.position
            if module_pos[0] != pos[0] or module_pos[1] != pos[1]:
                continue

            # Find linked module position
            if module.linked_module.position is not None:
                nodes.append(module.linked_module.position)

        # Remove the duplicate vertices from the final result
        filtered_neighbors = []
        for i in nodes:
            if i not in filtered_neighbors:
                filtered_neighbors.append(i)

        return filtered_neighbors

    def add_flow_segment(self, flow_segment):
        """
        Add flow segment to the list of flow segments
        """
        return self.flow_segments.append(flow_segment)

    def calculate(self):
        """
        Calculate how the energy flows to the modules
        """
        log('\n> Recalculating grid')

        most_important_modules = sorted(self.get_modules(), key=lambda v: v.priority, reverse=True)

        # Error out incorrect voltage
        for module in most_important_modules:
            if module.voltage is not module.table_section.voltage and module.voltage is not Voltages.ADAPTIVE:
                self.give_error_module(module)

        # Disable modules without attached flow segments
        if len(most_important_modules) >= 2:
            for module in most_important_modules:
                if not isinstance(module, DefaultModule) or module.remaining_power >= 0:
                    continue
        
                should_reset_power = True

                for other_module in most_important_modules:
                    if other_module is module:
                        continue
                    
                    if not isinstance(other_module, DefaultModule) or other_module.remaining_power <= 0:
                        continue

                    unparsed_path = self.astar(module.position, other_module.position)

                    if unparsed_path is None:
                        continue
                    
                    should_reset_power = False
                    break

                if should_reset_power:
                    log('- [' + module.name + '] has been reset as there are no paths to any other module!')
                    module.remaining_power = 0

        # Find paths for modules
        for module in most_important_modules:
            if not isinstance(
                    module, DefaultModule) or module.remaining_power <= 0:
                continue
            
            while module.remaining_power is None or module.remaining_power > 0:
                producing_module = module
                (consuming_module, path, distance) = self.get_closest_relevant_module(producing_module)
                if consuming_module is None:
                    break

                from_position = producing_module.position
                to_position = consuming_module.position

                power_consumption = min(
                    -consuming_module.remaining_power, producing_module.remaining_power)
                consuming_module.remaining_power += power_consumption
                producing_module.remaining_power -= power_consumption

                log('- [' + producing_module.name + '] => [' + consuming_module.name + '] Path from ' + str(from_position) + ' to ' + str(to_position) + ' (distance: ' + str(distance) + ')')

                desired_voltage = producing_module.voltage if producing_module.voltage is not Voltages.ADAPTIVE else consuming_module.voltage
                
                if desired_voltage is Voltages.ADAPTIVE:
                    desired_voltage = Voltages.HIGH


                self.flows.append(Flow(path, power_consumption, distance))
                self.generate_path(path, power_consumption, desired_voltage)
            
        self.smart_grid_app.reset_flow_config_timer()
        return
    
    def give_power_back_to_modules(self):
        for flow in self.flows:
            if flow.power is None:
                continue

            producing_module = self.get_module_on_position(flow.path[0])
            consuming_module = self.get_module_on_position(flow.path[-1])

            # Remove path
            if producing_module.table_section.voltage is Voltages.ERROR or consuming_module.table_section.voltage is Voltages.ERROR:
                if producing_module.remaining_power is None or consuming_module.remaining_power is None:
                    continue

                producing_module.remaining_power += flow.power
                consuming_module.remaining_power -= flow.power
                log("V [" + producing_module.name + "] X> [" + consuming_module.name + "] " + str(flow.power) + " power has been reverted")
                flow.power = None
        
        final_flows = [flow for flow in self.flows if flow.power is not None]
        removed_flows = [flow for flow in self.flows if flow.power is None]

        for removed_flow in removed_flows:
            for removed_node in removed_flow.path:
                should_remove_node = True
            
                for existing_flow in final_flows:
                    for existing_node in existing_flow.path:
                        if removed_node[0] is existing_node[0] and removed_node[1] is existing_node[1]:
                            should_remove_node = False
                            break
                    
                    if should_remove_node is False: break
                
                if should_remove_node is False: continue

                # Remove node
                for flow_segment in self.find_flow_segments_on_position(removed_node):
                    flow_segment.reset()

                    if flow_segment.table_section.voltage is Voltages.ERROR:
                        flow_segment.state = State.OFF
                    else:
                        flow_segment.state = State.PASSIVE
            
        
        self.flows = final_flows


        log("\n===== FINAL FLOWS =====")
        for flow in self.flows:
            from_position = flow.path[0]
            to_position = flow.path[-1]
            producing_module = self.get_module_on_position(from_position)
            consuming_module = self.get_module_on_position(to_position)
            distance = flow.distance


            log('- [' + producing_module.name + '] => [' + consuming_module.name + '] Path from ' + str(from_position) + ' to ' + str(to_position) + ' (distance: ' + str(distance) + ')')

        log("")

    def find_flow_segments_on_position(self, node):
        flow_segments = []
        for flow_segment in self.flow_segments:
            if (
                (flow_segment.start_pos[0] is node[0] and flow_segment.start_pos[1] is node[1]) or
                (flow_segment.end_pos[0] is node[0] and flow_segment.end_pos[1] is node[1])
            ): flow_segments.append(flow_segment)

        return flow_segments

    def give_error_module(self, module):
        """
        Show error to the flow segments that are connected to a module
        """
        for fs in self.flow_segments:
            if (fs.start_pos[0] != module.position[0]
                    or fs.start_pos[1] != module.position[1]) and (
                        fs.end_pos[0] != module.position[0]
                        or fs.end_pos[1] != module.position[1]):
                continue

            fs.state = State.ERROR

    def generate_path(self, found_path, power=None, voltage=None):
        """
        Returns the shortest path between two vertices
        """
        # Assign the directions for the appropriate flow segments to alter
        # future pathfinding
        for i, node in enumerate(found_path):
            if i > len(found_path) - 2:
                break

            next_node = found_path[i + 1]

            while True:
                flow_segments = self.flow_find_segments(node, next_node)

                if len(flow_segments) == 0:
                    break

                for flow_segment in flow_segments:
                    if flow_segment.start_pos == node:
                        flow_segment.direction = Direction.FORWARDS
                    else:
                        flow_segment.direction = Direction.BACKWARDS

                    flow_segment.state = State.ACTIVE
                    flow_segment.load = Load.NORMAL
                    flow_segment.speed = Speed.NORMAL
                    if voltage:
                        flow_segment.voltage = voltage

        return found_path

    def flow_find_segments(self, start_pos, end_pos, exclude_state = State.ACTIVE):
        """
        Find a flow segment based on given starting and ending vertices.
        """
        segments = []
        for flow_segment in self.flow_segments:
            if exclude_state is not None and flow_segment.state == exclude_state:
                continue

            if (flow_segment.start_pos == start_pos
                    and flow_segment.end_pos == end_pos) or (
                        flow_segment.start_pos == end_pos
                        and flow_segment.end_pos == start_pos):
                segments.append(flow_segment)

        return segments

    def get_closest_relevant_module(self, for_module, priority=1):
        """
        Find a producing module that can give energy to a consuming module, or find a consuming module that can receive energy from a producing module
        """
        available_modules = []
        for grid_module in self.get_modules():
            if not isinstance(grid_module, DefaultModule):
                continue

            # Grid module should have enough power
            if ((for_module.remaining_power < 0 and grid_module.remaining_power <= 0) or (for_module.remaining_power > 0 and grid_module.remaining_power >= 0)) or grid_module.priority != priority:
                continue

            available_modules.append(grid_module)

        if len(available_modules) is 0:
            return self.get_closest_relevant_module(for_module, priority - 1) if priority > 0 else (None, None, None)

        closest_module = None
        closest_module_distance = 99999999
        closest_module_path = None

        for module in available_modules:
            consuming_module = for_module
            producing_module = module

            if consuming_module.remaining_power > 0:
                consuming_module = module
                producing_module = for_module

            unparsed_path = self.astar(producing_module.position, consuming_module.position)
            if unparsed_path is None:
                continue

            path = list(unparsed_path)

            voltage = self.get_path_voltage(path)
            if voltage is Voltages.ERROR:
                continue

            distance = self.get_total_path_distance(path)

            if module.table_section is not for_module.table_section and (module.table_section.type is not 2 and for_module.table_section.type is not 2):
                distance += 5 + 5 * abs(module.table_section.voltage - for_module.table_section.voltage)

            set_new_closest_module = False

            if distance < closest_module_distance:
                set_new_closest_module = True
                
            elif distance is closest_module_distance:
                if module.remaining_power > closest_module.remaining_power:
                    set_new_closest_module = True
            
            if set_new_closest_module:
                closest_module = module
                closest_module_distance = distance
                closest_module_path = path

        return (closest_module, closest_module_path, closest_module_distance)

    def get_path_voltage(self, path):
        """
        Get voltage of the given path
        """
        voltage = None

        for i, node in enumerate(path):
            module = self.get_module_on_position(node)
            if module is None or module.voltage is Voltages.ADAPTIVE:
                continue

            if voltage is None:
                voltage = module.voltage
            elif voltage is not module.voltage:
                voltage = Voltages.ERROR
                break

            if not isinstance(module, TransformerModule):
                continue

            linked_module = module.linked_module

            if linked_module is None:
                continue

            next_node = path[i + 1]

            if self.get_module_on_position(next_node) is not linked_module:
                continue

            voltage = linked_module.voltage

        return voltage

    def get_module_on_position(self, pos):
        """
        Retrieve which module sits on a position
        """
        for module in self.get_modules():
            module_pos = module.position
            if module_pos[0] is pos[0] and module_pos[1] is pos[1]:
                return module

        return None

    def disable_flow(self, flow_id, enabled):
        """
        Disable a flow of the graph structure
        """
        self.flow_segments[flow_id].set_force_disabled(enabled)

    def reset(self):
        """
        Reset the state of the flow segments to allow recalculating
        """
        self.flows = []

        for flow_segment in self.flow_segments:
            flow_segment.reset()

        for module in self.get_modules():
            if not isinstance(module, DefaultModule):
                continue

            module.reset_power()

    def get_modules(self):
        """
        Function to retrieve all modules that are standing on the grid
        """
        modules = []
        for module in self.smart_grid_app.smart_grid_table.modules:
            if module.position is not None:
                modules.append(module)

        modules = sorted(modules, key=lambda module: module.time_placed, reverse=True)
        return modules
