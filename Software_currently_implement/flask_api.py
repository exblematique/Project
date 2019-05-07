#!/bin/env python2
import ast

from flask import Flask, request, jsonify
from flask.views import MethodView

from smart_grid_messaging import *
from smart_grid_table import *

_smart_grid_table = None
_add_message_func = None


class InvalidId(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class TableSectionView(MethodView):

    def get(self, table_id=None):
        global _smart_grid_table

        if table_id is None:
            tps = _smart_grid_table.get_table_sections()
            data = {
                "table_sections": [{
                    "id": tp.id,
                    "type": tp.type,
                    "pos": tp.pos,
                    "voltage": tp.get_voltage()
                } for tp in tps]
            }
        else:
            tp = _smart_grid_table.get_table_section(table_id)
            if tp is None:
                raise InvalidId('Table Section {0} does not exist'.format(
                    table_id), status_code=410)

            data = {
                "id": tp.id,
                "type": tp.type,
                "pos": tp.pos,
                "voltage": tp.get_voltage()
            }

        return jsonify(data)

    def put(self):
        put_data = request.get_json()
        id, pos = put_data.get('id', None), put_data.get('pos', None)

        _smart_grid_table.get_table_section(id).set_position(pos)
        _smart_grid_table.write_table_config()
        return jsonify(request.get_json())


class TableSectionModuleView(MethodView):

    def get(self, table_section_id):
        global _smart_grid_table
        tp = _smart_grid_table.get_table_section(table_section_id)
        if tp is None:
            raise InvalidId('Table Section {0} does not exist'.format(
                table_section_id), status_code=410)
        modules = tp.get_placed_modules()
        data = {
            "modules": [{
                "id": m.id,
                "locationId": location,
                "name": m.name
            } for location, m in enumerate(modules) if m is not None]
        }

        return jsonify(data)


class ModuleView(MethodView):

    def get(self, module_id=None):
        global _smart_grid_table
        if module_id is None:
            modules = _smart_grid_table.get_modules()
            data = {
                "modules": [{
                    "id": m.id
                } for m in modules if isinstance(m, DefaultModule)],
                "transformers": [{
                    "id": m.id
                } for m in modules if isinstance(m, ConnectionModule)]
            }
            return jsonify(data)
        else:
            module = _smart_grid_table.get_module(module_id)
            if module is None:
                raise InvalidId('Module {0} does not exist'.format(
                    module_id), status_code=410)
            if isinstance(module, DefaultModule):
                data = {
                    "id": module.id,
                    "name": module.name,
                    "voltage": module.get_voltage(string=True),
                    "type": module.type,
                    "power": module.get_power(),
                }
                return jsonify(data)
            else:
                raise InvalidId('Module {0} is not a DefaultModule'.format(
                    module_id), status_code=410)

class ModuleConfigView(MethodView):

    def get(self, module_id, config_id=None):
        global _smart_grid_table
        module = _smart_grid_table.get_module(module_id)
        if module is None:
            raise InvalidId('Module {0} does not exist'.format(
                module_id), status_code=410)

        if config_id is None:
            configs = module.get_configurations()
            data = {
                "configurations": [{
                    "id": config.get_config_id(),
                    "min": config.get_min_value(),
                    "max": config.get_max_value(),
                    "value": config.get_value(),
                    "name": config.get_name(),
                    "role": config.get_role(string=True)
                } for config in configs]
            }
            return jsonify(data)
        else:
            config = module.get_configuration(config_id)
            if config is None:
                raise InvalidId('Config {0} does not exist'.format(
                    config_id), status_code=410)

            data = {
                "id": config.get_config_id(),
                "min": config.get_min_value(),
                "max": config.get_max_value(),
                "value": config.get_value(),
                "name": config.get_name(),
                "role": config.get_role(string=True)
            }
            return jsonify(data)

    def put(self, module_id, config_id):
        global _smart_grid_table

        module = _smart_grid_table.get_module(module_id)
        if module is None:
            raise InvalidId('Module {0} does not exist'.format(
                module_id), status_code=410)

        config = module.get_configuration(config_id)
        if config is None:
            raise InvalidId('Config {0} does not exist'.format(
                config_id), status_code=410)

        put_data = request.get_json()
        new_value = int(put_data.get('value'))

        if new_value > config.get_max_value():
            raise InvalidId('Value {0} for Config {1} was higher than allowed'.format(
                new_value, config_id), status_code=410)
        if new_value < config.get_min_value():
            raise InvalidId('Value {0} for Config {1} was lower than allowed'.format(
                new_value, config_id), status_code=410)

        s_message = SmartMessage(
            MessageTypes.CONFIG_CHANGED,
            (module_id, config_id, new_value))

        _add_message_func(s_message)

        data = {
            "id": config.get_config_id(),
            "min": config.get_min_value(),
            "max": config.get_max_value(),
            "value": new_value,
            "name": config.get_name(),
            "role": config.get_role(string=True)
        }
        return jsonify(data)


class FlowSegmentColorView(MethodView):

    def put(self, color_id):
        color_ids = [COLOR_DICT[c]['id'] for c in COLOR_DICT]
        if color_id not in color_ids:
            raise InvalidId('Color id {0} does not exist'.format(
                color_id), status_code=410)

        put_data = request.get_json()
        rgb = put_data.get('rgb', '')

        if not self.valid_rgb(rgb):
            raise InvalidId('RGB {0} not valid'.format(rgb), status_code=410)

        for color in COLOR_DICT:
            if COLOR_DICT[color]['id'] is color_id:
                formatted = self.format_to_rgb(rgb)
                COLOR_DICT[color]['color'] = (formatted['r'], formatted['g'], formatted['b'], 1.0)

        s_message = SmartMessage(MessageTypes.COLOR_CHANGED, (color_id, rgb))
        _add_message_func(s_message)

        return jsonify(put_data)

    def get(self):

        data = {
            "all": [
                self.format_to_hex(color)
                for color in ALL_COLORS_DICT
            ],
            "current": [{
                "color": self.format_to_hex(COLOR_DICT[color]['color']),
                "id": COLOR_DICT[color]['id']
            } for color in COLOR_DICT]
        }
        return jsonify(data)

    def valid_rgb(self, rgb):
        """
        RGB should be string of 6 characters. + check for hex string
        """
        if len(rgb) is 6:
            try:
                int(rgb, 16)
                return True
            except:
                pass
        return False

    @staticmethod
    def format_to_rgb(hex):
        """
        Formats a hexadecimal value to a RGB color.
        """
        r, g, b = bytearray.fromhex(hex)

        r = round(float(r) / 255, 1) if r > 0 else 0
        g = round(float(g) / 255, 1) if g > 0 else 0
        b = round(float(b) / 255, 1) if b > 0 else 0

        return {'r': r, 'g': g, 'b': b}

    def format_to_hex(self, color):
        """
        Formats an RGB value to a hexadecimal color.
        """
        return '%02x%02x%02x' % (color[0] * 255, color[1] * 255, color[2] * 255)


class PowerBoundaryView(MethodView):

    def get(self):
        data = {
            'boundaries': VOLTAGE_POWER_LOAD_BOUNDARIES
        }

        return jsonify(data)

    def put(self):
        put_data = request.get_json()
        voltage, load, value = put_data.get('voltage', None), put_data.get(
            'load', None), put_data.get('value', None)
        if voltage not in VOLTAGE_POWER_LOAD_BOUNDARIES:
            raise InvalidId('Voltage {0} not supported'.format(
                voltage), status_code=410)
        if load not in VOLTAGE_POWER_LOAD_BOUNDARIES[voltage]:
            raise InvalidId('Load {0} not supported'.format(
                load), status_code=410)
        if not self.validate_value(value, load):
            raise InvalidId('Invalid value {0}'.format(value), status_code=410)

        s_message = SmartMessage(
            MessageTypes.POWER_BOUNDARIES_CHANGED, (voltage, load, value))
        _add_message_func(s_message)

        return jsonify(put_data)

    def validate_value(self, value, load):
        """
        value should be > 0 if load is critical,
        value should be between 0-1 if load is high
        """
        if load is Load.HIGH:
            value = float(value)
            return True if 0 < value < 1 else False
        if load is Load.CRITICAL:
            value = int(value)
            return True if value > 0 else False
        return False


class Reboot(MethodView):

    def put(self):
        s_message = SmartMessage(MessageTypes.RESET_TABLES)
        _add_message_func(s_message)
        return jsonify(enabled="")


class GridView(MethodView):

    def get(self, table_id=None):
        global _smart_grid_table

        grid = _smart_grid_table.grid

        data = {"flow_segments": [], "modules": []}

        # If the table ID is not set, return all segments and modules
        # of the complete setup, else return only the data relevant to
        # the specified table.
        if table_id is None:
            for flow_segment in grid.flow_segments:
                data["flow_segments"].append(self.format_segment(flow_segment))

            for grid_module in (module for module in grid.get_modules() if isinstance(module, DefaultModule)):
                    data["modules"].append(self.format_module(grid_module))
        else:
            for flow_segment in (segment for segment in grid.flow_segments if segment.table_section.id is table_id):
                data["flow_segments"].append(self.format_segment(flow_segment))

            for grid_module in (module for module in grid.get_modules() if isinstance(module, DefaultModule)):
                if grid_module.table_section.id is not None and grid_module.table_section.id is table_id:
                    data["modules"].append(self.format_module(grid_module))

        return jsonify(data)

    def format_segment(self, segment):
        data = {
            "start_pos": segment.start_pos,
            "end_pos": segment.end_pos,
            "direction": segment.direction,
            "enabled": segment.enabled,
            "table_section": segment.table_section.id,
            "load": segment.load
        }
        return data

    def format_module(self, module):
        data = {
            "pos": module.position,
            "remainingPower": module.remaining_power if hasattr(module, 'remaining_power') else 0,
            "table_section": module.table_section.id if module.table_section else None,
            "module_id": module.id,
            "type": module.type
        }
        return data

class FlowSegmentState(MethodView):

    def put(self, table_id, flow_id):
        global _smart_grid_table
        grid = _smart_grid_table.grid

        put_data = request.get_json()
        enabled = bool(ast.literal_eval(put_data.get('enabled', None).title()))
        grid.disable_flow(table_id, flow_id, enabled)
        _smart_grid_table.calculate()

        return jsonify(enabled=enabled)


class NeighboringTables(MethodView):

    def get(self, table_id):
        global _smart_grid_table
        neighbours = _smart_grid_table.get_neighbours(table_id)

        data = ({
            "top": neighbours[0],
            "bottom": neighbours[1],
            "right": neighbours[2],
            "left": neighbours[3]
        })
        return jsonify(data)


class ApiServer(Flask):

    def __init__(self, smart_grid_table, add_message_func):
        super(ApiServer, self).__init__(__name__)

        # Set smart grid table / message func so views can reach it
        global _smart_grid_table
        _smart_grid_table = smart_grid_table
        global _add_message_func
        _add_message_func = add_message_func

        # Add endpoints
        view_func = TableSectionView.as_view('table_sections')
        self.add_endpoint('/api/tablesections/', view_func, ['GET', 'PUT'])
        self.add_endpoint('/api/tablesections/<int:table_id>/', view_func, ['GET'])

        view_func = TableSectionModuleView.as_view('table_sections_modules')
        self.add_endpoint(
            '/api/tablesections/<int:table_section_id>/modules/', view_func, ['GET'])

        view_func = ModuleView.as_view('modules')
        self.add_endpoint('/api/modules/', view_func, ['GET'])
        self.add_endpoint('/api/modules/<int:module_id>/', view_func, ['GET'])

        view_func = ModuleConfigView.as_view('modules_configs')
        self.add_endpoint(
            '/api/modules/<int:module_id>/configs/', view_func, ['GET'])
        self.add_endpoint(
            '/api/modules/<int:module_id>/configs/<int:config_id>/', view_func, ['GET', 'PUT'])

        view_func = FlowSegmentColorView.as_view('flow_colors')
        self.add_endpoint('/api/flowcolor/', view_func, ['GET'])
        self.add_endpoint('/api/flowcolor/<int:color_id>/', view_func, ['PUT'])

        view_func = PowerBoundaryView.as_view('power_boundaries')
        self.add_endpoint('/api/powerboundaries/', view_func, ['GET', 'PUT'])

        view_func = GridView.as_view('grid')
        self.add_endpoint('/api/grid/', view_func, ['GET'])
        self.add_endpoint('/api/grid/<int:table_id>/', view_func, ['GET'])

        view_func = Reboot.as_view('Reboot')
        self.add_endpoint('/api/reboot/', view_func, ['PUT'])

        view_func = FlowSegmentState.as_view('FlowSegmentState')
        self.add_endpoint('/api/flowsegment/<int:table_id>/<int:flow_id>/', view_func, ['PUT'])

        view_func = NeighboringTables.as_view('table_neighbours')
        self.add_endpoint('/api/neighbours/<int:table_id>/', view_func, ['GET'])

        @self.errorhandler(InvalidId)
        def handle_invalid_usage(error):
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response

    def add_endpoint(self, url, view_func, methods):
        self.add_url_rule(url, methods=methods, view_func=view_func)


if __name__ == "__main__":
    def print_msg(msg):
        print(msg)


    # Import tests values
    from test_scripts.values_for_testing import *

    # Create table (also creates modules)
    table = SmartGridTable()

    # Connect a table (table_id, child_id, table_type)
    table.table_connected(table_1_id, None, None)
    table.table_connected(table_2_id, None, None)
    table.table_connected(table_3_id, None, None)
    table_section1 = table.get_table_section(table_1_id)
    table_section2 = table.get_table_section(table_2_id)
    table_section3 = table.get_table_section(table_3_id)

    # Place modules on Table Section (table_id, location_id, module_id)
    table.module_placed(table_1_id, module_location_west, module_low)
    table.module_placed(table_1_id, module_location_northwest, module_low2)
    table.module_placed(table_1_id, module_location_northeast, module_low3)

    # connect neighbor. table_neighbor_changed(table_id, location_id,
    # connected_neighbor_id)
    table.table_neighbor_changed(
        table_1_id, table_conn_point_north, table_2_conn_south)
    table.table_neighbor_changed(
        table_2_id, table_conn_point_south, table_1_conn_north)

    # connect by transformers. module_placed(table_id, location_id, module_id)
    table.module_placed(table_3_id, module_location_east,
                        transformer_high)  # Place transformer high
    table.module_placed(table_2_id, module_location_west,
                        transformer_mediumH)  # Place transformer medium

    ApiServer(table, print_msg).run(host='0.0.0.0')