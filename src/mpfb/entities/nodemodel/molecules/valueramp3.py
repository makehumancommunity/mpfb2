from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.valueramp3")
_GROUP_NAME = "MpfbValueRamp3"

class MpfbValueRamp3(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [1078.6741943359375, 88.35167694091797]
        nodes["Group Input"].location = [-1205.7359619140625, -213.122314453125]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("ZeroStopValue", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("BetweenStop1Value", socket_type="NodeSocketFloat", default_value=0.000)
        self.add_input_socket("BetweenStop2Value", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("OneStopValue", socket_type="NodeSocketFloat", default_value=0.000)
        self.add_input_socket("BetweenStop1Position", socket_type="NodeSocketFloat", default_value=0.330)
        self.add_input_socket("BetweenStop2Position", socket_type="NodeSocketFloat", default_value=0.660)

        self.add_output_socket("Value", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["Map Range"] = self.createShaderNodeMapRange(name="Map Range", x=-599.264, y=747.069, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Math.003"] = self.createShaderNodeMath(name="Math.003", x=113.891, y=314.191, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-274.094, y=795.858, Value=1.000, Value_001=0.500, Value_002=0.500, operation='SUBTRACT', use_clamp=False)
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-87.121, y=615.953, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=-88.290, y=441.009, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.004"] = self.createShaderNodeMath(name="Math.004", x=112.572, y=516.639, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=True)
        nodes["Math.005"] = self.createShaderNodeMath(name="Math.005", x=363.944, y=418.687, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Map Range.002"] = self.createShaderNodeMapRange(name="Map Range.002", x=-616.414, y=-824.414, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Math.013"] = self.createShaderNodeMath(name="Math.013", x=119.374, y=-420.156, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Math.014"] = self.createShaderNodeMath(name="Math.014", x=-356.746, y=-945.977, Value=1.000, Value_001=0.500, Value_002=0.500, operation='SUBTRACT', use_clamp=False)
        nodes["Math.015"] = self.createShaderNodeMath(name="Math.015", x=-73.032, y=-589.624, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.016"] = self.createShaderNodeMath(name="Math.016", x=-79.240, y=-770.616, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.017"] = self.createShaderNodeMath(name="Math.017", x=119.606, y=-632.490, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=True)
        nodes["Map Range.001"] = self.createShaderNodeMapRange(name="Map Range.001", x=-754.610, y=-371.864, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Math.007"] = self.createShaderNodeMath(name="Math.007", x=-498.670, y=-439.349, Value=1.000, Value_001=0.500, Value_002=0.500, operation='SUBTRACT', use_clamp=False)
        nodes["Math.009"] = self.createShaderNodeMath(name="Math.009", x=-214.639, y=-345.106, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.008"] = self.createShaderNodeMath(name="Math.008", x=-269.020, y=-124.953, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.010"] = self.createShaderNodeMath(name="Math.010", x=-267.701, y=70.622, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Math.011"] = self.createShaderNodeMath(name="Math.011", x=-40.028, y=-206.981, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=True)
        nodes["Math.020"] = self.createShaderNodeMath(name="Math.020", x=346.075, y=41.645, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.019"] = self.createShaderNodeMath(name="Math.019", x=145.825, y=111.387, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["Math.012"] = self.createShaderNodeMath(name="Math.012", x=159.648, y=-64.649, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.006"] = self.createShaderNodeMath(name="Math.006", x=636.757, y=96.029, Value=0.500, Value_001=0.000, Value_002=0.500, operation='ADD', use_clamp=True)
        nodes["Math.021"] = self.createShaderNodeMath(name="Math.021", x=858.464, y=94.332, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=False)
        nodes["Math.018"] = self.createShaderNodeMath(name="Math.018", x=352.839, y=-522.793, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)

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
        self.add_link(nodes["Math.021"], "Value", nodes["Group Output"], "Value")
        self.add_link(nodes["Map Range.001"], "Result", nodes["Math.007"], "Value_001")
        self.add_link(nodes["Math.007"], "Value", nodes["Math.008"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop1Value", nodes["Math.008"], "Value_001")
        self.add_link(nodes["Map Range.001"], "Result", nodes["Math.009"], "Value_001")
        self.add_link(nodes["Group Input"], "BetweenStop1Position", nodes["Math.010"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.010"], "Value")
        self.add_link(nodes["Math.008"], "Value", nodes["Math.011"], "Value")
        self.add_link(nodes["Math.009"], "Value", nodes["Math.011"], "Value_001")
        self.add_link(nodes["Math.010"], "Value", nodes["Math.012"], "Value")
        self.add_link(nodes["Math.011"], "Value", nodes["Math.012"], "Value_001")
        self.add_link(nodes["Map Range.002"], "Result", nodes["Math.014"], "Value_001")
        self.add_link(nodes["Math.014"], "Value", nodes["Math.015"], "Value")
        self.add_link(nodes["Map Range.002"], "Result", nodes["Math.016"], "Value_001")
        self.add_link(nodes["Math.015"], "Value", nodes["Math.017"], "Value")
        self.add_link(nodes["Math.016"], "Value", nodes["Math.017"], "Value_001")
        self.add_link(nodes["Math.013"], "Value", nodes["Math.018"], "Value")
        self.add_link(nodes["Math.017"], "Value", nodes["Math.018"], "Value_001")
        self.add_link(nodes["Group Input"], "BetweenStop2Position", nodes["Map Range.001"], "From Max")
        self.add_link(nodes["Group Input"], "BetweenStop2Value", nodes["Math.009"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop2Position", nodes["Map Range.002"], "From Min")
        self.add_link(nodes["Group Input"], "Value", nodes["Map Range.002"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop2Value", nodes["Math.015"], "Value_001")
        self.add_link(nodes["Group Input"], "OneStopValue", nodes["Math.016"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop2Position", nodes["Math.013"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.013"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStop2Position", nodes["Math.019"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.019"], "Value")
        self.add_link(nodes["Math.019"], "Value", nodes["Math.020"], "Value")
        self.add_link(nodes["Math.012"], "Value", nodes["Math.020"], "Value_001")
        self.add_link(nodes["Math.020"], "Value", nodes["Math.006"], "Value_001")
        self.add_link(nodes["Math.006"], "Value", nodes["Math.021"], "Value")
        self.add_link(nodes["Math.018"], "Value", nodes["Math.021"], "Value_001")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbValueRamp3(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopValue=None, BetweenStop1Value=None, BetweenStop2Value=None, OneStopValue=None, BetweenStop1Position=None, BetweenStop2Position=None):
#         return self._molecule_singletons["MpfbValueRamp3"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopValue=ZeroStopValue, BetweenStop1Value=BetweenStop1Value, BetweenStop2Value=BetweenStop2Value, OneStopValue=OneStopValue, BetweenStop1Position=BetweenStop1Position, BetweenStop2Position=BetweenStop2Position)



