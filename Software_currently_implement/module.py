import time

from file_writer import read_contents_from_file, save_module_config
from logger import log
from settings import *


def load_module_info():
    """
    Read and return modules from the config/moduleConfig.json file. 
    """

    data = read_contents_from_file(MODULE_CONFIG_FILE)
    modules = []

    # Load all configuration types
    config_types = [
        ModuleConfigurationType(  # id, name, min_value, max_value, role, voltage
            config["id"],
            config["name"],
            config["min"],
            config["max"],
            Roles.str_to_enum(config["role"]),
            Voltages.str_to_enum(config["voltage"])
        ) for config in data["configTypes"]
    ]

    for c in config_types:
        log('config', c)

    # Load default modules
    for module in data["modules"]:
        # Create a list of module configurations
        module_configs = [
            ModuleConfiguration(  # config_type, value
                next((t for t in config_types if t.id == mc["type"])),
                mc["value"]
            ) for mc in module["configurations"]
        ]
        # Create the module
        module = DefaultModule(  # id, name, type, voltage, configurations
            module["id"],
            module["name"],
            module["type"],
            Voltages.str_to_enum(module["voltage"]),
            module_configs)

        modules.append(module)

    # Load transformer modules
    for module in data["transformers"]:
        # Get linked transformer
        linked = next((m for m in modules if m.id == module["linked"]), None)

        # Create the module
        module = TransformerModule(  # id, name, voltage, linked module
            module["id"],
            module["name"],
            Voltages.str_to_enum(module["voltage"]),
            linked)

        modules.append(module)

    # Load transformer modules
    for module in data["wireModules"]:
        # Get linked transformer
        linked = next((m for m in modules if m.id == module["linked"]), None)

        # Create the module
        module = WireModule(  # id, name, voltage, linked module
            module["id"],
            module["name"],
            Voltages.str_to_enum(module["voltage"]),
            linked)

        modules.append(module)

    # Load transformer modules
    for module in data["importModules"]:
        # Create the module
        module = ImportExportModule(  # id, name, voltage
            module["id"],
            module["name"],
            Voltages.str_to_enum(module["voltage"]))

        modules.append(module)

    [log('loaded module:', module) for module in modules]

    return modules


class ModuleConfigurationType(object):
    """
    Module configuration type is a configuration for a module, like an electric
    car or wind turbine. Each configuration has its own min and max value.
    """

    def __init__(self, id, name, min_value, max_value, role, voltage):
        super(ModuleConfigurationType, self).__init__()
        self.id = id
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.role = role  # production or consumption
        self.voltage = voltage

    def get_role(self):
        return self.role  # production or consumption

    def __repr__(self):
        return '{0} <{1}-{2}>)'.format(self.name, self.min_value, self.max_value)


class ModuleConfiguration(object):
    """
    Module configuration object, has module config type and value
    """

    def __init__(self, config_type, value):
        super(ModuleConfiguration, self).__init__()
        self.config_type = config_type
        self.value = int(float(value))

    def get_value(self):
        return self.value

    def get_name(self):
        return self.config_type.name

    def set_value(self, value):
        self.value = int(float(value))

    def get_voltage(self):
        return self.config_type.voltage

    def get_role(self, string=False):
        return Roles.enum_to_str(self.config_type.role) if string else self.config_type.role

    def get_min_value(self):
        return self.config_type.min_value

    def get_max_value(self):
        return self.config_type.max_value

    def get_config_id(self):
        return self.config_type.id

class Module(object):
    """
    Module object, contains id, name, voltage.
    """

    def __init__(self, id, name, voltage, type = None):
        super(Module, self).__init__()
        self.id = id
        self.name = name
        self.type = type
        self.voltage = voltage
        self.table_section = None
        self.time_placed = None
        self.position = None
        self.priority = 1

    def get_voltage(self, string=False):
        return Voltages.enum_to_str(self.voltage) if string else self.voltage

    def set_table_section(self, table):
        if self.table_section is not None:
            self.table_section.remove_module(self)

        self.table_section = table

        if self.table_section is not None:
            self.table_section.add_module(self)

        self.time_placed = time.time()

    def __repr__(self):
        return '{0} ({1})'.format(self.name, self.id)


class DefaultModule(Module):
    """
    Default module, like house or windmill. Has configurations to define the 
    production and/or consumption of a module.
    """

    def __init__(self, id, name, type, voltage, configurations):
        super(DefaultModule, self).__init__(id, name, voltage, type)
        self.configurations = configurations
        self.remaining_power = 0

        if voltage is Voltages.ADAPTIVE:
            self.priority = 0
        self.reset_power()

    def get_production(self):
        return sum([c.get_value() for c in self.configurations if c.get_role() is Roles.PRODUCTION])

    def get_consumption(self):
        return sum([c.get_value() for c in self.configurations if c.get_role() is Roles.CONSUMPTION])

    def reset_power(self):
        self.remaining_power = -self.get_power()

    def get_power(self):
        return self.get_consumption() - self.get_production()

    def get_configurations(self):
        return self.configurations

    def get_configuration(self, config_id):
        config = next(
            (c for c in self.configurations if c.get_config_id() == config_id), None)
        return config

    def save_configuration(self, config_id, value):
        save_module_config(MODULE_CONFIG_FILE, self.id, config_id, value)

        for config in self.configurations:
            if config.get_config_id() is config_id:
                config.set_value(value)
                break


class ConnectionModule(Module):
    """
    Connection module, is linked with another transformer module
    """

    def __init__(self, id, name, voltage, linked_module):
        super(ConnectionModule, self).__init__(id, name, voltage)
        self.linked_module = linked_module
        if linked_module is not None:
            linked_module.set_linked_module(self)

    def set_linked_module(self, linked_module):
        self.linked_module = linked_module


class TransformerModule(ConnectionModule):
    """
    Transformer module, is linked with another transformer module
    """

    def __init__(self, id, name, voltage, linked_module):
        super(TransformerModule, self).__init__(
            id, name, voltage, linked_module)


class WireModule(ConnectionModule):
    """
    Transformer module, is linked with another transformer module
    """

    def __init__(self, id, name, voltage, linked_module):
        super(WireModule, self).__init__(id, name, voltage, linked_module)
        self.index = 0

    def set_table_section(self, table):
        super(WireModule, self).set_table_section(table)
        self.index = 0
        self.linked_module.index = 0


class ImportExportModule(ConnectionModule):
    """
    Import/export module
    """

    def __init__(self, id, name, voltage):
        linked = ConnectionModule(0, "non-existing", Voltages.ERROR, None)
        super(ImportExportModule, self).__init__(id, name, voltage, linked)
