from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.shaderrouter4")
_GROUP_NAME = "MpfbShaderRouter4"

class MpfbShaderRouter4(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [555.4822387695312, -85.3839111328125]
        nodes["Group Input"].location = [-724.9921264648438, -59.5100212097168]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Threshold1", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Threshold2", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Threshold3", socket_type="NodeSocketFloat", default_value=0.800)
        self.add_input_socket("Section1Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section2Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section3Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section4Shader", socket_type="NodeSocketShader")

        self.add_output_socket("Shader", socket_type="NodeSocketShader")

        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-396.522, y=281.572, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["Mix Shader"] = self.createShaderNodeMixShader(name="Mix Shader", x=-185.473, y=172.083, Fac=0.5)
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-190.453, y=39.220, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix Shader.001"] = self.createShaderNodeMixShader(name="Mix Shader.001", x=113.715, y=-27.146, Fac=0.5)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=111.323, y=-152.247, Value=0.500, Value_001=0.800, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix Shader.002"] = self.createShaderNodeMixShader(name="Mix Shader.002", x=369.191, y=-293.111, Fac=0.5)

        self.add_link(nodes["Group Input"], "Value", nodes["Math"], "Value")
        self.add_link(nodes["Group Input"], "Threshold1", nodes["Math"], "Value_001")
        self.add_link(nodes["Math"], "Value", nodes["Mix Shader"], "Fac")
        self.add_link(nodes["Mix Shader"], "Shader", nodes["Mix Shader.001"], "Shader")
        self.add_link(nodes["Math.001"], "Value", nodes["Mix Shader.001"], "Fac")
        self.add_link(nodes["Group Input"], "Section1Shader", nodes["Mix Shader"], "Shader_001")
        self.add_link(nodes["Group Input"], "Section2Shader", nodes["Mix Shader"], "Shader")
        self.add_link(nodes["Group Input"], "Threshold2", nodes["Math.001"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Group Input"], "Section3Shader", nodes["Mix Shader.001"], "Shader_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.002"], "Value")
        self.add_link(nodes["Mix Shader.001"], "Shader", nodes["Mix Shader.002"], "Shader")
        self.add_link(nodes["Mix Shader.002"], "Shader", nodes["Group Output"], "Shader")
        self.add_link(nodes["Math.002"], "Value", nodes["Mix Shader.002"], "Fac")
        self.add_link(nodes["Group Input"], "Section4Shader", nodes["Mix Shader.002"], "Shader_001")
        self.add_link(nodes["Group Input"], "Threshold3", nodes["Math.002"], "Value_001")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbShaderRouter4(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold1=None, Threshold2=None, Threshold3=None, Section1Shader=None, Section2Shader=None, Section3Shader=None, Section4Shader=None):
#         return self._molecule_singletons["MpfbShaderRouter4"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold1=Threshold1, Threshold2=Threshold2, Threshold3=Threshold3, Section1Shader=Section1Shader, Section2Shader=Section2Shader, Section3Shader=Section3Shader, Section4Shader=Section4Shader)


