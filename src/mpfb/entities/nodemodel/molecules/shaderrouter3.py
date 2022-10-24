from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.shaderrouter3")
_GROUP_NAME = "MpfbShaderRouter3"

class MpfbShaderRouter3(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [411.4923095703125, -43.98564147949219]
        nodes["Group Input"].location = [-539.6157836914062, 46.57303237915039]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=0.5)
        self.add_input_socket("Threshold1", socket_type="NodeSocketFloat", default_value=0.33)
        self.add_input_socket("Threshold2", socket_type="NodeSocketFloat", default_value=0.66)
        self.add_input_socket("Section1Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section2Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section3Shader", socket_type="NodeSocketShader")

        self.add_output_socket("Shader", socket_type="NodeSocketShader")

        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-247.3587646484375, y=219.4750213623047, Value=0.5, Value_001=0.5, Value_002=0.5, operation='LESS_THAN', use_clamp=False)
        nodes["Mix Shader"] = self.createShaderNodeMixShader(name="Mix Shader", x=-27.68780517578125, y=70.31269836425781, Fac=0.5)
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-24.045127868652344, y=-74.62506866455078, Value=0.5, Value_001=0.5, Value_002=0.5, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix Shader.001"] = self.createShaderNodeMixShader(name="Mix Shader.001", x=195.62586975097656, y=-236.7242889404297, Fac=0.5)

        self.add_link(nodes["Group Input"], "Value", nodes["Math"], "Value")
        self.add_link(nodes["Group Input"], "Threshold1", nodes["Math"], "Value_001")
        self.add_link(nodes["Mix Shader.001"], "Shader", nodes["Group Output"], "Shader")
        self.add_link(nodes["Math"], "Value", nodes["Mix Shader"], "Fac")
        self.add_link(nodes["Mix Shader"], "Shader", nodes["Mix Shader.001"], "Shader")
        self.add_link(nodes["Math.001"], "Value", nodes["Mix Shader.001"], "Fac")
        self.add_link(nodes["Group Input"], "Section1Shader", nodes["Mix Shader"], "Shader_001")
        self.add_link(nodes["Group Input"], "Section2Shader", nodes["Mix Shader"], "Shader")
        self.add_link(nodes["Group Input"], "Threshold2", nodes["Math.001"], "Value_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Group Input"], "Section3Shader", nodes["Mix Shader.001"], "Shader_001")