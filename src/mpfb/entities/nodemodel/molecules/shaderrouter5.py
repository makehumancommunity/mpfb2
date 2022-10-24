from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.shaderrouter5")
_GROUP_NAME = "MpfbShaderRouter5"

class MpfbShaderRouter5(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [831.4348754882812, -199.4665985107422]
        nodes["Group Input"].location = [-724.9921264648438, -59.5100212097168]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=0.5)
        self.add_input_socket("Threshold1", socket_type="NodeSocketFloat", default_value=0.2)
        self.add_input_socket("Threshold2", socket_type="NodeSocketFloat", default_value=0.4)
        self.add_input_socket("Threshold3", socket_type="NodeSocketFloat", default_value=0.6)
        self.add_input_socket("Threshold4", socket_type="NodeSocketFloat", default_value=0.8)
        self.add_input_socket("Section1Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section2Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section3Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section4Shader", socket_type="NodeSocketShader")
        self.add_input_socket("Section5Shader", socket_type="NodeSocketShader")

        self.add_output_socket("Shader", socket_type="NodeSocketShader")

        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-396.5220031738281, y=281.5724182128906, Value=0.5, Value_001=0.5, Value_002=0.5, operation='LESS_THAN', use_clamp=False)
        nodes["Mix Shader"] = self.createShaderNodeMixShader(name="Mix Shader", x=-185.47320556640625, y=172.08343505859375, Fac=0.5)
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-190.4526824951172, y=39.22016525268555, Value=0.5, Value_001=0.5, Value_002=0.5, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix Shader.001"] = self.createShaderNodeMixShader(name="Mix Shader.001", x=113.71541595458984, y=-27.145559310913086, Fac=0.5)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=111.32268524169922, y=-152.24681091308594, Value=0.5, Value_001=0.800000011920929, Value_002=0.5, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix Shader.002"] = self.createShaderNodeMixShader(name="Mix Shader.002", x=369.1913757324219, y=-293.1106262207031, Fac=0.5)
        nodes["Mix Shader.003"] = self.createShaderNodeMixShader(name="Mix Shader.003", x=607.6591186523438, y=-546.8049926757812, Fac=0.5)
        nodes["Math.003"] = self.createShaderNodeMath(name="Math.003", x=372.9194030761719, y=-424.2900695800781, Value=0.5, Value_001=0.800000011920929, Value_002=0.5, operation='GREATER_THAN', use_clamp=False)

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
        self.add_link(nodes["Math.002"], "Value", nodes["Mix Shader.002"], "Fac")
        self.add_link(nodes["Group Input"], "Section4Shader", nodes["Mix Shader.002"], "Shader_001")
        self.add_link(nodes["Group Input"], "Threshold3", nodes["Math.002"], "Value_001")
        self.add_link(nodes["Mix Shader.003"], "Shader", nodes["Group Output"], "Shader")
        self.add_link(nodes["Mix Shader.002"], "Shader", nodes["Mix Shader.003"], "Shader")
        self.add_link(nodes["Math.003"], "Value", nodes["Mix Shader.003"], "Fac")
        self.add_link(nodes["Group Input"], "Section5Shader", nodes["Mix Shader.003"], "Shader_001")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.003"], "Value")
        self.add_link(nodes["Group Input"], "Threshold4", nodes["Math.003"], "Value_001")