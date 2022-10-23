from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.withindistance")
_GROUP_NAME = "MpfbWithinDistance"

class MpfbWithinDistance(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        self.add_input_socket("Coordinate1", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_input_socket("Coordinate2", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_input_socket("MaxDist", socket_type="NodeSocketFloat", default_value=0.5)

        self.add_output_socket("WithinDistance", socket_type="NodeSocketFloat")
        self.add_output_socket("ActualDistance", socket_type="NodeSocketFloat")

        nodes["Math"] = self.createShaderNodeMath(name="Math", x=81.0936508178711, y=170.7898406982422, operation='LESS_THAN')
        nodes["Vector Math"] = self.createShaderNodeVectorMath(name="Vector Math", x=-119.4195785522461, y=-94.73934173583984, operation='DISTANCE')

        self.add_link(nodes["Group Input"], "Coordinate1", nodes["Vector Math"], "Vector")
        self.add_link(nodes["Group Input"], "Coordinate2", nodes["Vector Math"], "Vector_001")
        self.add_link(nodes["Group Input"], "MaxDist", nodes["Math"], "Value_001")
        self.add_link(nodes["Math"], "Value", nodes["Group Output"], "WithinDistance")
        self.add_link(nodes["Vector Math"], "Value", nodes["Group Output"], "ActualDistance")
        self.add_link(nodes["Vector Math"], "Value", nodes["Math"], "Value")
