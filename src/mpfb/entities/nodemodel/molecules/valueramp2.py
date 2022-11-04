from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.valueramp2")
_GROUP_NAME = "MpfbValueRamp2"

class MpfbValueRamp2(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [800.6748657226562, 71.568359375]
        nodes["Group Input"].location = [-872.1455078125, 16.128082275390625]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("ZeroStopValue", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("BetweenStop1Value", socket_type="NodeSocketFloat", default_value=0.000)
        self.add_input_socket("OneStopValue", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("BetweenStop1Position", socket_type="NodeSocketFloat", default_value=1.000)

        self.add_output_socket("Value", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["Map Range"] = self.createShaderNodeMapRange(name="Map Range", x=-597.990, y=521.639, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Math.003"] = self.createShaderNodeMath(name="Math.003", x=115.164, y=88.762, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["Math.006"] = self.createShaderNodeMath(name="Math.006", x=575.236, y=44.747, Value=0.500, Value_001=0.000, Value_002=0.500, operation='ADD', use_clamp=True)
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-272.821, y=570.429, Value=1.000, Value_001=0.500, Value_002=0.500, operation='SUBTRACT', use_clamp=False)
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-85.848, y=390.524, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=-87.016, y=215.580, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Map Range.001"] = self.createShaderNodeMapRange(name="Map Range.001", x=-619.152, y=-525.678, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Math.010"] = self.createShaderNodeMath(name="Math.010", x=116.636, y=-121.420, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Math.007"] = self.createShaderNodeMath(name="Math.007", x=-359.484, y=-647.242, Value=1.000, Value_001=0.500, Value_002=0.500, operation='SUBTRACT', use_clamp=False)
        nodes["Math.004"] = self.createShaderNodeMath(name="Math.004", x=113.845, y=291.209, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=True)
        nodes["Math.008"] = self.createShaderNodeMath(name="Math.008", x=-75.770, y=-290.888, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.009"] = self.createShaderNodeMath(name="Math.009", x=-81.978, y=-471.880, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.011"] = self.createShaderNodeMath(name="Math.011", x=116.868, y=-333.754, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=True)
        nodes["Math.005"] = self.createShaderNodeMath(name="Math.005", x=365.217, y=193.257, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.012"] = self.createShaderNodeMath(name="Math.012", x=350.101, y=-224.057, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)

        self.add_link(nodes["Group Input"], "Value", nodes["Map Range"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop1Position", nodes["Map Range"], "From Max")
        self.add_link(nodes["Group Input"], "BetweenStop1Position", nodes["Map Range.001"], "From Min")
        self.add_link(nodes["Group Input"], "Value", nodes["Map Range.001"], "Value")
        self.add_link(nodes["Map Range"], "Result", nodes["Math"], "Value_001")
        self.add_link(nodes["Group Input"], "ZeroStopValue", nodes["Math.001"], "Value_001")
        self.add_link(nodes["Math"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Map Range"], "Result", nodes["Math.002"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop1Value", nodes["Math.002"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.003"], "Value")
        self.add_link(nodes["Math.001"], "Value", nodes["Math.004"], "Value")
        self.add_link(nodes["Math.002"], "Value", nodes["Math.004"], "Value_001")
        self.add_link(nodes["Math.004"], "Value", nodes["Math.005"], "Value")
        self.add_link(nodes["Math.005"], "Value", nodes["Math.006"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop1Position", nodes["Math.003"], "Value_001")
        self.add_link(nodes["Math.003"], "Value", nodes["Math.005"], "Value_001")
        self.add_link(nodes["Math.006"], "Value", nodes["Group Output"], "Value")
        self.add_link(nodes["Map Range.001"], "Result", nodes["Math.007"], "Value_001")
        self.add_link(nodes["Math.007"], "Value", nodes["Math.008"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop1Value", nodes["Math.008"], "Value_001")
        self.add_link(nodes["Map Range.001"], "Result", nodes["Math.009"], "Value_001")
        self.add_link(nodes["Group Input"], "OneStopValue", nodes["Math.009"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop1Position", nodes["Math.010"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.010"], "Value")
        self.add_link(nodes["Math.008"], "Value", nodes["Math.011"], "Value")
        self.add_link(nodes["Math.009"], "Value", nodes["Math.011"], "Value_001")
        self.add_link(nodes["Math.010"], "Value", nodes["Math.012"], "Value")
        self.add_link(nodes["Math.011"], "Value", nodes["Math.012"], "Value_001")
        self.add_link(nodes["Math.012"], "Value", nodes["Math.006"], "Value_001")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbValueRamp2(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopValue=None, BetweenStop1Value=None, OneStopValue=None, BetweenStop1Position=None):
#         return self._molecule_singletons["MpfbValueRamp2"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopValue=ZeroStopValue, BetweenStop1Value=BetweenStop1Value, OneStopValue=OneStopValue, BetweenStop1Position=BetweenStop1Position)
