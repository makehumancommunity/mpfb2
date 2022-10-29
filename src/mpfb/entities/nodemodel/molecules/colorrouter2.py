from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.colorrouter2")
_GROUP_NAME = "MpfbColorRouter2"

class MpfbColorRouter2(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [345.2333679199219, -122.97506713867188]
        nodes["Group Input"].location = [-383.4490661621094, -122.97506713867188]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Threshold", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Section1Color", socket_type="NodeSocketColor", default_value=[1.0, 0.0, 0.0010608520824462175, 1.0])
        self.add_input_socket("Section2Color", socket_type="NodeSocketColor", default_value=[0.0, 1.0, 0.0012432460207492113, 1.0])

        self.add_output_socket("Color", socket_type="NodeSocketColor", default_value=[0.0, 0.0, 0.0, 0.0])

        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-111.902, y=18.856, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix"] = self.createShaderNodeMixRGB(name="Mix", x=109.245, y=-89.274, Fac=0.5, Color1=[0.5, 0.5, 0.5, 1.0], Color2=[0.5, 0.5, 0.5, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)

        self.add_link(nodes["Group Input"], "Value", nodes["Math"], "Value")
        self.add_link(nodes["Group Input"], "Threshold", nodes["Math"], "Value_001")
        self.add_link(nodes["Mix"], "Color", nodes["Group Output"], "Color")
        self.add_link(nodes["Math"], "Value", nodes["Mix"], "Fac")
        self.add_link(nodes["Group Input"], "Section1Color", nodes["Mix"], "Color1")
        self.add_link(nodes["Group Input"], "Section2Color", nodes["Mix"], "Color2")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbColorRouter2(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold=None, Section1Color=None, Section2Color=None):
#         return self._molecule_singletons["MpfbColorRouter2"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold=Threshold, Section1Color=Section1Color, Section2Color=Section2Color)
