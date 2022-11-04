from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.characterinfo")
_GROUP_NAME = "MpfbCharacterInfo"

class MpfbCharacterInfo(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Input"].location = [-344.1031494140625, 73.5843276977539]
        nodes["Group Output"].location = [380.4578552246094, 83.66437530517578]


        self.add_output_socket("scale_factor", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("gender", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("age", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("height", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("weight", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("muscle", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["scale_factor"] = self.createShaderNodeAttribute(name="scale_factor", label="scale_factor", x=-144.103, y=537.266, attribute_name='MPFB_GEN_scale_factor', attribute_type='OBJECT')
        nodes["gender"] = self.createShaderNodeAttribute(name="gender", label="gender", x=-144.103, y=352.801, attribute_name='MPFB_HUM_gender', attribute_type='OBJECT')
        nodes["weight"] = self.createShaderNodeAttribute(name="weight", label="weight", x=-144.103, y=-200.593, attribute_name='MPFB_HUM_weight', attribute_type='OBJECT')
        nodes["muscle"] = self.createShaderNodeAttribute(name="muscle", label="muscle", x=-142.088, y=-390.097, attribute_name='MPFB_HUM_muscle', attribute_type='OBJECT')
        nodes["age"] = self.createShaderNodeAttribute(name="age", label="age", x=-143.095, y=169.345, attribute_name='MPFB_HUM_age', attribute_type='OBJECT')
        nodes["height"] = self.createShaderNodeAttribute(name="height", label="height", x=-140.072, y=-15.120, attribute_name='MPFB_HUM_height', attribute_type='OBJECT')

        self.add_link(nodes["scale_factor"], "Fac", nodes["Group Output"], "scale_factor")
        self.add_link(nodes["gender"], "Fac", nodes["Group Output"], "gender")
        self.add_link(nodes["age"], "Fac", nodes["Group Output"], "age")
        self.add_link(nodes["height"], "Fac", nodes["Group Output"], "height")
        self.add_link(nodes["weight"], "Fac", nodes["Group Output"], "weight")
        self.add_link(nodes["muscle"], "Fac", nodes["Group Output"], "muscle")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbCharacterInfo(self, x=0.0, y=0.0, name=None, label=None):
#         return self._molecule_singletons["MpfbCharacterInfo"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)
