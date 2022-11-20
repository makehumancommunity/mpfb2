from mpfb.services.logservice import LogService
from .cell import Cell

import bpy

_LOG = LogService.get_logger("nodemodel.ssscontrol")
_GROUP_NAME = "MpfbSSSControl"

class MpfbSSSControl(Cell):
    def __init__(self):
        _LOG.trace("Constructing Cell for", _GROUP_NAME)
        Cell.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [176.7465, -5.4503]
        nodes["Group Input"].location = [-821.2342, -3.7404]

        self.add_input_socket("SubsurfaceColor", socket_type="NodeSocketColor", default_value=[0.5, 0.5, 0.5, 1.0])
        self.add_input_socket("SubsurfaceStrength", socket_type="NodeSocketFloat", default_value=0.0000)
        self.add_input_socket("SubsurfaceRadiusMultiplyer", socket_type="NodeSocketFloat", default_value=1.0000)
        self.add_input_socket("SubsurfaceIor", socket_type="NodeSocketFloat", default_value=1.4000)

        self.add_output_socket("SubsurfaceColor", socket_type="NodeSocketColor", default_value=[0.5, 0.5, 0.5, 1.0])
        self.add_output_socket("SubsurfaceRadius", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_output_socket("SubsurfaceStrength", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("SubsurfaceIor", socket_type="NodeSocketFloat", default_value=1.399999976158142)

        nodes["Vector Math"] = self.createShaderNodeVectorMath(name="Vector Math", x=-13.2536, y=215.3835, Vector=[1.0, 0.20000000298023224, 0.10000000149011612], Vector_001=[0.0, 0.0, 0.0], Vector_002=[0.0, 0.0, 0.0], Scale=1.0000, operation='MULTIPLY')
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-527.8343, y=190.5644, Value=0.5000, Value_001=0.5000, Value_002=0.5000, operation='MULTIPLY', use_clamp=False)
        nodes["Combine XYZ"] = self.createShaderNodeCombineXYZ(name="Combine XYZ", x=-279.0480, y=202.1848, X=0.0000, Y=0.0000, Z=0.0000)
        nodes["Group.003"] = self.createMpfbCharacterInfo(name="Group.003", x=-794.2700, y=296.3641)

        self.add_link(nodes["Vector Math"], "Vector", nodes["Group Output"], "SubsurfaceRadius")
        self.add_link(nodes["Math"], "Value", nodes["Combine XYZ"], "X")
        self.add_link(nodes["Math"], "Value", nodes["Combine XYZ"], "Y")
        self.add_link(nodes["Math"], "Value", nodes["Combine XYZ"], "Z")
        self.add_link(nodes["Combine XYZ"], "Vector", nodes["Vector Math"], "Vector_001")
        self.add_link(nodes["Group Input"], "SubsurfaceRadiusMultiplyer", nodes["Math"], "Value_001")
        self.add_link(nodes["Group Input"], "SubsurfaceStrength", nodes["Group Output"], "SubsurfaceStrength")
        self.add_link(nodes["Group Input"], "SubsurfaceColor", nodes["Group Output"], "SubsurfaceColor")
        self.add_link(nodes["Group Input"], "SubsurfaceIor", nodes["Group Output"], "SubsurfaceIor")
        self.add_link(nodes["Group.003"], "Output_0", nodes["Math"], "Value")



# --- paste this in the CellNodeManager class def
#
#     def createMpfbSSSControl(self, x=0.0, y=0.0, name=None, label=None, SubsurfaceColor=None, SubsurfaceStrength=None, SubsurfaceRadiusMultiplyer=None, SubsurfaceIor=None):
#         return self._cell_singletons["MpfbSSSControl"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, SubsurfaceColor=SubsurfaceColor, SubsurfaceStrength=SubsurfaceStrength, SubsurfaceRadiusMultiplyer=SubsurfaceRadiusMultiplyer, SubsurfaceIor=SubsurfaceIor)
