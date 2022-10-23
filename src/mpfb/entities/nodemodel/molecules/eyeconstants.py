from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.eyecentercoordinates")
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
        self.add_output_socket("Eyeball size", socket_type="NodeSocketFloat", default_value=0.285)

        nodes["RightEye"] = self.createShaderNodeCombineXYZ(name="RightEye", x=-238.25181579589844, y=108.7710189819336, X=0.7049999833106995, Y=0.699999988079071, Z=0.0)
        nodes["LeftEye"] = self.createShaderNodeCombineXYZ(name="LeftEye", x=-238.9952850341797, y=244.32997131347656, X=0.29499998688697815, Y=0.30000001192092896, Z=0.0)
        nodes["EyeballSize"] = self.createShaderNodeValue(name="EyeballSize", label="EyeballSize", x=-239.6428680419922, y=-26.80507469177246, Value=0.2849999964237213)

        self.add_link(nodes["LeftEye"], "Vector", nodes["Group Output"], "Left eye coord")
        self.add_link(nodes["RightEye"], "Vector", nodes["Group Output"], "Right eye coord")
        self.add_link(nodes["EyeballSize"], "Value", nodes["Group Output"], "Eyeball size")

    def create_instance(self, node_tree, name=None, color=None, label=None, x=None, y=None):
        pass


