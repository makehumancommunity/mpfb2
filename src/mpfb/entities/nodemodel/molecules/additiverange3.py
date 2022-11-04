from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.additiverange3")
_GROUP_NAME = "MpfbAdditiveRange3"

class MpfbAdditiveRange3(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [1235.4036865234375, -228.23077392578125]
        nodes["Group Input"].location = [-1301.69189453125, 10.54866886138916]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Section1Size", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Section2Size", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Section3Size", socket_type="NodeSocketFloat", default_value=0.500)

        self.add_output_socket("NormalizedSectionValue", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("TotalSectionSize", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("WithinSection1", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("WithinSection2", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("WithinSection3", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-281.460, y=279.457, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=-284.326, y=111.532, Value=0.500, Value_001=0.000, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Math.005"] = self.createShaderNodeMath(name="Math.005", x=407.502, y=328.894, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["WithinSection1"] = self.createShaderNodeMath(name="WithinSection1", label="WithinSection1", x=-33.607, y=193.119, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Map Range"] = self.createShaderNodeMapRange(name="Map Range", x=174.071, y=470.783, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=422.416, y=-315.394, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Map Range.001"] = self.createShaderNodeMapRange(name="Map Range.001", x=188.053, y=-458.819, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["WithinSection2"] = self.createShaderNodeMath(name="WithinSection2", label="WithinSection2", x=-37.630, y=-356.359, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.003"] = self.createShaderNodeMath(name="Math.003", x=-285.957, y=-284.085, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["Math.004"] = self.createShaderNodeMath(name="Math.004", x=-289.756, y=-465.763, Value=0.500, Value_001=0.000, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Math.008"] = self.createShaderNodeMath(name="Math.008", x=413.347, y=-801.250, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Map Range.002"] = self.createShaderNodeMapRange(name="Map Range.002", x=178.984, y=-944.675, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Math.009"] = self.createShaderNodeMath(name="Math.009", x=-295.027, y=-769.941, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["Math.010"] = self.createShaderNodeMath(name="Math.010", x=-298.825, y=-951.619, Value=0.500, Value_001=0.000, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Section12Size"] = self.createShaderNodeMath(name="Section12Size", label="Section12Size", x=-907.063, y=-163.234, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=False)
        nodes["TotalSectionSize"] = self.createShaderNodeMath(name="TotalSectionSize", label="TotalSectionSize", x=-616.655, y=-827.357, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=False)
        nodes["Math.006"] = self.createShaderNodeMath(name="Math.006", x=711.712, y=23.944, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=False)
        nodes["WithinSection3"] = self.createShaderNodeMath(name="WithinSection3", label="WithinSection3", x=-46.699, y=-842.215, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["Math.007"] = self.createShaderNodeMath(name="Math.007", x=970.028, y=-431.118, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=False)

        self.add_link(nodes["Group Input"], "Section1Size", nodes["Section12Size"], "Value")
        self.add_link(nodes["Group Input"], "Section2Size", nodes["Section12Size"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.002"], "Value")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Group Input"], "Section1Size", nodes["Math.001"], "Value_001")
        self.add_link(nodes["Math.002"], "Value", nodes["WithinSection1"], "Value_001")
        self.add_link(nodes["Math.001"], "Value", nodes["WithinSection1"], "Value")
        self.add_link(nodes["WithinSection1"], "Value", nodes["Group Output"], "WithinSection1")
        self.add_link(nodes["Section12Size"], "Value", nodes["Math.003"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.003"], "Value")
        self.add_link(nodes["Group Input"], "Section1Size", nodes["Math.004"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.004"], "Value")
        self.add_link(nodes["Math.003"], "Value", nodes["WithinSection2"], "Value")
        self.add_link(nodes["Math.004"], "Value", nodes["WithinSection2"], "Value_001")
        self.add_link(nodes["WithinSection2"], "Value", nodes["Group Output"], "WithinSection2")
        self.add_link(nodes["Group Input"], "Section1Size", nodes["Map Range"], "From Max")
        self.add_link(nodes["Group Input"], "Value", nodes["Map Range"], "Value")
        self.add_link(nodes["Section12Size"], "Value", nodes["Map Range.001"], "From Max")
        self.add_link(nodes["Group Input"], "Section1Size", nodes["Map Range.001"], "From Min")
        self.add_link(nodes["Group Input"], "Value", nodes["Map Range.001"], "Value")
        self.add_link(nodes["WithinSection2"], "Value", nodes["Math"], "Value")
        self.add_link(nodes["Map Range.001"], "Result", nodes["Math"], "Value_001")
        self.add_link(nodes["WithinSection1"], "Value", nodes["Math.005"], "Value_001")
        self.add_link(nodes["Map Range"], "Result", nodes["Math.005"], "Value")
        self.add_link(nodes["Math.005"], "Value", nodes["Math.006"], "Value")
        self.add_link(nodes["Math"], "Value", nodes["Math.006"], "Value_001")
        self.add_link(nodes["Section12Size"], "Value", nodes["TotalSectionSize"], "Value")
        self.add_link(nodes["Group Input"], "Section3Size", nodes["TotalSectionSize"], "Value_001")
        self.add_link(nodes["Math.009"], "Value", nodes["WithinSection3"], "Value")
        self.add_link(nodes["Math.010"], "Value", nodes["WithinSection3"], "Value_001")
        self.add_link(nodes["WithinSection3"], "Value", nodes["Math.008"], "Value")
        self.add_link(nodes["Map Range.002"], "Result", nodes["Math.008"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.009"], "Value")
        self.add_link(nodes["TotalSectionSize"], "Value", nodes["Math.009"], "Value_001")
        self.add_link(nodes["Section12Size"], "Value", nodes["Math.010"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.010"], "Value")
        self.add_link(nodes["Group Input"], "Value", nodes["Map Range.002"], "Value")
        self.add_link(nodes["Section12Size"], "Value", nodes["Map Range.002"], "From Min")
        self.add_link(nodes["TotalSectionSize"], "Value", nodes["Map Range.002"], "From Max")
        self.add_link(nodes["Math.006"], "Value", nodes["Math.007"], "Value")
        self.add_link(nodes["Math.008"], "Value", nodes["Math.007"], "Value_001")
        self.add_link(nodes["TotalSectionSize"], "Value", nodes["Group Output"], "TotalSectionSize")
        self.add_link(nodes["WithinSection3"], "Value", nodes["Group Output"], "WithinSection3")
        self.add_link(nodes["Math.007"], "Value", nodes["Group Output"], "NormalizedSectionValue")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbAdditiveRange3(self, x=0.0, y=0.0, name=None, label=None, Value=None, Section1Size=None, Section2Size=None, Section3Size=None):
#         return self._molecule_singletons["MpfbAdditiveRange3"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Section1Size=Section1Size, Section2Size=Section2Size, Section3Size=Section3Size)