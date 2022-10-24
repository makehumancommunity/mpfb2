from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.massadd")
_GROUP_NAME = "MpfbMassAdd"

class MpfbMassAdd(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [588.496337890625, -45.0581169128418]
        nodes["Group Input"].location = [-795.1384887695312, 119.04366302490234]

        self.add_input_socket("Value1", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_input_socket("Value2", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_input_socket("Value3", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_input_socket("Value4", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_input_socket("Value5", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_input_socket("Value6", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_input_socket("Value7", socket_type="NodeSocketFloat", default_value=0.0)

        self.add_output_socket("Sum", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-551.3284301757812, y=251.3260498046875, Value=0.0, Value_001=0.0, Value_002=0.0, operation='ADD', use_clamp=False)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=-371.0575256347656, y=196.3446502685547, Value=0.0, Value_001=0.0, Value_002=0.0, operation='ADD', use_clamp=False)
        nodes["Math.003"] = self.createShaderNodeMath(name="Math.003", x=-188.9339141845703, y=137.77940368652344, Value=0.0, Value_001=0.0, Value_002=0.0, operation='ADD', use_clamp=False)
        nodes["Math.004"] = self.createShaderNodeMath(name="Math.004", x=-6.97913122177124, y=79.0684585571289, Value=0.0, Value_001=0.0, Value_002=0.0, operation='ADD', use_clamp=False)
        nodes["Math.005"] = self.createShaderNodeMath(name="Math.005", x=177.58213806152344, y=20.327484130859375, Value=0.0, Value_001=0.0, Value_002=0.0, operation='ADD', use_clamp=False)
        nodes["Math.006"] = self.createShaderNodeMath(name="Math.006", x=356.5506591796875, y=-44.94025802612305, Value=0.0, Value_001=0.0, Value_002=0.0, operation='ADD', use_clamp=False)

        self.add_link(nodes["Group Input"], "Value1", nodes["Math.001"], "Value")
        self.add_link(nodes["Group Input"], "Value2", nodes["Math.001"], "Value_001")
        self.add_link(nodes["Group Input"], "Value3", nodes["Math.002"], "Value_001")
        self.add_link(nodes["Group Input"], "Value4", nodes["Math.003"], "Value_001")
        self.add_link(nodes["Group Input"], "Value5", nodes["Math.004"], "Value_001")
        self.add_link(nodes["Math.001"], "Value", nodes["Math.002"], "Value")
        self.add_link(nodes["Math.002"], "Value", nodes["Math.003"], "Value")
        self.add_link(nodes["Math.003"], "Value", nodes["Math.004"], "Value")
        self.add_link(nodes["Math.004"], "Value", nodes["Math.005"], "Value")
        self.add_link(nodes["Math.005"], "Value", nodes["Math.006"], "Value")
        self.add_link(nodes["Math.006"], "Value", nodes["Group Output"], "Sum")
        self.add_link(nodes["Group Input"], "Value6", nodes["Math.005"], "Value_001")
        self.add_link(nodes["Group Input"], "Value7", nodes["Math.006"], "Value_001")