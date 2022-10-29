from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.eyeconstants")
_GROUP_NAME = "MpfbEyeConstants"

class MpfbEyeConstants(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Input"].location = [-529.9879760742188, 78.62328338623047]
        nodes["Group Output"].location = [146.0699920654297, 110.87899780273438]


        self.add_output_socket("Left eye coord", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_output_socket("Right eye coord", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_output_socket("Eyeball size", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["RightEye"] = self.createShaderNodeCombineXYZ(name="RightEye", x=-238.252, y=108.771, X=0.705, Y=0.700, Z=0.000)
        nodes["LeftEye"] = self.createShaderNodeCombineXYZ(name="LeftEye", x=-238.995, y=244.330, X=0.295, Y=0.300, Z=0.000)
        nodes["EyeballSize"] = self.createShaderNodeValue(name="EyeballSize", label="EyeballSize", x=-239.643, y=-26.805, Value=0.285)

        self.add_link(nodes["LeftEye"], "Vector", nodes["Group Output"], "Left eye coord")
        self.add_link(nodes["RightEye"], "Vector", nodes["Group Output"], "Right eye coord")
        self.add_link(nodes["EyeballSize"], "Value", nodes["Group Output"], "Eyeball size")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbEyeConstants(self, x=0.0, y=0.0, name=None, label=None):
#         return self._molecule_singletons["MpfbEyeConstants"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)
