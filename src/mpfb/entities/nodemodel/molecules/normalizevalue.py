from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.normalizevalue")
_GROUP_NAME = "MpfbNormalizeValue"

class MpfbNormalizeValue(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [398.9898986816406, 39.8891487121582]
        nodes["Group Input"].location = [-689.7285766601562, 39.091365814208984]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("IncomingMin", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("IncomingMax", socket_type="NodeSocketFloat", default_value=0.500)

        self.add_output_socket("NormalizedValue", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("IsWithinRange", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-320.634, y=-213.445, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-319.038, y=-49.899, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=-101.258, y=-120.826, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.004"] = self.createShaderNodeMath(name="Math.004", x=78.191, y=240.569, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Map Range"] = self.createShaderNodeMapRange(name="Map Range", x=-323.838, y=218.613, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')

        self.add_link(nodes["Group Input"], "Value", nodes["Map Range"], "Value")
        self.add_link(nodes["Math.002"], "Value", nodes["Group Output"], "IsWithinRange")
        self.add_link(nodes["Math.004"], "Value", nodes["Group Output"], "NormalizedValue")
        self.add_link(nodes["Math.001"], "Value", nodes["Math.002"], "Value_001")
        self.add_link(nodes["Math"], "Value", nodes["Math.002"], "Value")
        self.add_link(nodes["Math.002"], "Value", nodes["Math.004"], "Value_001")
        self.add_link(nodes["Map Range"], "Result", nodes["Math.004"], "Value")
        self.add_link(nodes["Group Input"], "Value", nodes["Math"], "Value")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Group Input"], "IncomingMin", nodes["Math.001"], "Value_001")
        self.add_link(nodes["Group Input"], "IncomingMax", nodes["Math"], "Value_001")
        self.add_link(nodes["Group Input"], "IncomingMin", nodes["Map Range"], "From Min")
        self.add_link(nodes["Group Input"], "IncomingMax", nodes["Map Range"], "From Max")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbNormalizeValue(self, x=0.0, y=0.0, name=None, label=None, Value=None, IncomingMin=None, IncomingMax=None):
#         return self._molecule_singletons["MpfbNormalizeValue"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, IncomingMin=IncomingMin, IncomingMax=IncomingMax)
