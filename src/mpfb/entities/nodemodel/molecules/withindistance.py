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
        nodes["Group Output"].location = [392.9463806152344, 41.3276252746582]
        nodes["Group Input"].location = [-397.9847106933594, 96.76712799072266]

        self.add_input_socket("Coordinate1", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_input_socket("Coordinate2", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_input_socket("MaxDist", socket_type="NodeSocketFloat", default_value=0.500)

        self.add_output_socket("WithinDistance", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("ActualDistance", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["Vector Math"] = self.createShaderNodeVectorMath(name="Vector Math", x=-157.711, y=193.546, Vector=[0.0, 0.0, 0.0], Vector_001=[0.0, 0.0, 0.0], Vector_002=[0.0, 0.0, 0.0], Scale=1.000, operation='DISTANCE')
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=64.971, y=30.679, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)

        self.add_link(nodes["Group Input"], "Coordinate1", nodes["Vector Math"], "Vector")
        self.add_link(nodes["Group Input"], "Coordinate2", nodes["Vector Math"], "Vector_001")
        self.add_link(nodes["Group Input"], "MaxDist", nodes["Math"], "Value_001")
        self.add_link(nodes["Math"], "Value", nodes["Group Output"], "WithinDistance")
        self.add_link(nodes["Vector Math"], "Value", nodes["Group Output"], "ActualDistance")
        self.add_link(nodes["Vector Math"], "Value", nodes["Math"], "Value")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbWithinDistance(self, x=0.0, y=0.0, name=None, label=None, Coordinate1=None, Coordinate2=None, MaxDist=None):
#         return self._molecule_singletons["MpfbWithinDistance"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Coordinate1=Coordinate1, Coordinate2=Coordinate2, MaxDist=MaxDist)


