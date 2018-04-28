# import sys
# import os

# import pyverilog_parser
# import verilog_util


class Port():
    def __init__(self, name, direction='output', comment="", size=1, default=None):
        self.name = name
        self.size = size
        self.direction = direction
        self.default = default
        self.connection = self.name
        self.comment = comment
        self.customise = None

    def __str__(self):
        return "Port: {:30}{:30}{:8}{}".format(self.name, self.connection, self.direction, self.size)


# TODO: Leave this here????
def find_port(name, port_list):
    # Check for capitalisation errors
    for port in port_list:
        if (port.name != name) & (port.name.lower() == name.lower()):
            print port.name,
            print name
            raise NameError("Port names only differ by capitalisation : {} - {}".format(port.name, name))

    for port in port_list:
        if port.name == name:
            return True
    return False


# TODO: Leave this here????
def remove_port_from_list(port_name, port_list):
    for p in port_list:
        if p['name'] == port_name:
            port_list.remove(p)
            return

    raise NameError("Tried to remove a port from list that isn't in the list: " + port_name)
