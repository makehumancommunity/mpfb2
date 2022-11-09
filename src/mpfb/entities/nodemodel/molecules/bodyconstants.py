from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.bodyconstants")
_GROUP_NAME = "MpfbBodyConstants"

class MpfbBodyConstants(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Input"].location = [-854.1890, -67.3678]
        nodes["Group Output"].location = [541.3774, 219.5866]


        self.add_output_socket("RightNippleCoordinate", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_output_socket("LeftNippleCoordinate", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_output_socket("NavelCoordinate", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_output_socket("RightMouthCorner", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_output_socket("LeftMouthCorner", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_output_socket("MouthCenter", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])

        nodes["RightNipple"] = self.createShaderNodeCombineXYZ(name="RightNipple", label="RightNipple", x=-677.5740, y=301.1666, X=0.3252, Y=0.699, Z=0.0000)
        nodes["LeftNipple"] = self.createShaderNodeCombineXYZ(name="LeftNipple", label="LeftNipple", x=-678.5061, y=167.5498, X=0.4358, Y=0.699, Z=0.0000)
        nodes["Navel"] = self.createShaderNodeCombineXYZ(name="Navel", label="Navel", x=-678.4309, y=30.1713, X=0.3806, Y=0.5634, Z=0.0000)
        nodes["RightMouthCorner"] = self.createShaderNodeCombineXYZ(name="RightMouthCorner", label="RightMouthCorner", x=-678.8247, y=-101.1879, X=0.9100, Y=0.4650, Z=0.0000)
        nodes["LeftMouthCorner"] = self.createShaderNodeCombineXYZ(name="LeftMouthCorner", label="LeftMouthCorner", x=-686.2820, y=-230.7953, X=0.9100, Y=0.5020, Z=0.0000)
        nodes["Separate XYZ.001"] = self.createShaderNodeSeparateXYZ(name="Separate XYZ.001", x=-302.9055, y=-326.1380, Vector=[0.0, 0.0, 0.0])
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-88.2530, y=-178.9764, Value=0.5000, Value_001=0.5000, Value_002=0.5000, operation='ADD', use_clamp=False)
        nodes["Combine XYZ"] = self.createShaderNodeCombineXYZ(name="Combine XYZ", x=305.1906, y=-27.2413, X=0.0000, Y=0.0000, Z=0.0000)
        nodes["Separate XYZ"] = self.createShaderNodeSeparateXYZ(name="Separate XYZ", x=-301.9734, y=-180.6793, Vector=[0.0, 0.0, 0.0])
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=105.3512, y=-169.8206, Value=0.5000, Value_001=2.0000, Value_002=0.5000, operation='DIVIDE', use_clamp=False)

        self.add_link(nodes["RightNipple"], "Vector", nodes["Group Output"], "RightNippleCoordinate")
        self.add_link(nodes["LeftNipple"], "Vector", nodes["Group Output"], "LeftNippleCoordinate")
        self.add_link(nodes["Navel"], "Vector", nodes["Group Output"], "NavelCoordinate")
        self.add_link(nodes["RightMouthCorner"], "Vector", nodes["Group Output"], "RightMouthCorner")
        self.add_link(nodes["LeftMouthCorner"], "Vector", nodes["Group Output"], "LeftMouthCorner")
        self.add_link(nodes["RightMouthCorner"], "Vector", nodes["Separate XYZ"], "Vector")
        self.add_link(nodes["LeftMouthCorner"], "Vector", nodes["Separate XYZ.001"], "Vector")
        self.add_link(nodes["Separate XYZ.001"], "Y", nodes["Math"], "Value_001")
        self.add_link(nodes["Separate XYZ"], "Y", nodes["Math"], "Value")
        self.add_link(nodes["Math"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Separate XYZ"], "X", nodes["Combine XYZ"], "X")
        self.add_link(nodes["Math.001"], "Value", nodes["Combine XYZ"], "Y")
        self.add_link(nodes["Combine XYZ"], "Vector", nodes["Group Output"], "MouthCenter")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbBodyConstants(self, x=0.0, y=0.0, name=None, label=None):
#         return self._molecule_singletons["MpfbBodyConstants"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

