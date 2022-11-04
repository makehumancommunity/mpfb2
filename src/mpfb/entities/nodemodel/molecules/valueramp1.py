from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.valueramp1")
_GROUP_NAME = "MpfbValueRamp1"

class MpfbValueRamp1(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [353.2497253417969, 140.11270141601562]
        nodes["Group Input"].location = [-878.1918334960938, 154.22476196289062]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("ZeroStopValue", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("OneStopValue", socket_type="NodeSocketFloat", default_value=0.000)

        self.add_output_socket("Value", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-529.752, y=349.477, Value=1.000, Value_001=0.500, Value_002=0.500, operation='SUBTRACT', use_clamp=True)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=-253.685, y=115.538, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-254.693, y=294.963, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.003"] = self.createShaderNodeMath(name="Math.003", x=38.809, y=206.874, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=True)

        self.add_link(nodes["Group Input"], "Value", nodes["Math"], "Value_001")
        self.add_link(nodes["Math"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Group Input"], "ZeroStopValue", nodes["Math.001"], "Value_001")
        self.add_link(nodes["Group Input"], "OneStopValue", nodes["Math.002"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.002"], "Value")
        self.add_link(nodes["Math.001"], "Value", nodes["Math.003"], "Value")
        self.add_link(nodes["Math.002"], "Value", nodes["Math.003"], "Value_001")
        self.add_link(nodes["Math.003"], "Value", nodes["Group Output"], "Value")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbValueRamp1(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopValue=None, OneStopValue=None):
#         return self._molecule_singletons["MpfbValueRamp1"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopValue=ZeroStopValue, OneStopValue=OneStopValue)
