from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.colorrouter3")
_GROUP_NAME = "MpfbColorRouter3"

class MpfbColorRouter3(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [477.5954895019531, -111.78630828857422]
        nodes["Group Input"].location = [-650.9696655273438, -146.2849884033203]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=0.5)
        self.add_input_socket("Threshold1", socket_type="NodeSocketFloat", default_value=0.33)
        self.add_input_socket("Threshold2", socket_type="NodeSocketFloat", default_value=0.66)
        self.add_input_socket("Section1Color", socket_type="NodeSocketColor", default_value=[1.0, 0.0, 0.0, 1.0])
        self.add_input_socket("Section2Color", socket_type="NodeSocketColor", default_value=[0.0, 1.0, 0.0, 1.0])
        self.add_input_socket("Section3Color", socket_type="NodeSocketColor", default_value=[0.0, 0.0, 1.0, 1.0])

        self.add_output_socket("Color", socket_type="NodeSocketColor", default_value=[0.0, 0.0, 0.0, 0.0])

        nodes["Mix"] = self.createShaderNodeMixRGB(name="Mix", x=-175.98594665527344, y=62.70615768432617, Fac=0.5, Color1=[0.5, 0.5, 0.5, 1.0], Color2=[0.5, 0.5, 0.5, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-371.9658203125, y=119.5547103881836, Value=0.5, Value_001=0.5, Value_002=0.5, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix.001"] = self.createShaderNodeMixRGB(name="Mix.001", x=103.65616607666016, y=-19.316675186157227, Fac=0.5, Color1=[0.5, 0.5, 0.5, 1.0], Color2=[0.5, 0.5, 0.5, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-171.558349609375, y=-199.3248748779297, Value=0.5, Value_001=0.5, Value_002=0.5, operation='GREATER_THAN', use_clamp=False)

        self.add_link(nodes["Group Input"], "Value", nodes["Math"], "Value")
        self.add_link(nodes["Group Input"], "Threshold1", nodes["Math"], "Value_001")
        self.add_link(nodes["Mix.001"], "Color", nodes["Group Output"], "Color")
        self.add_link(nodes["Math"], "Value", nodes["Mix"], "Fac")
        self.add_link(nodes["Group Input"], "Section1Color", nodes["Mix"], "Color1")
        self.add_link(nodes["Group Input"], "Section2Color", nodes["Mix"], "Color2")
        self.add_link(nodes["Mix"], "Color", nodes["Mix.001"], "Color1")
        self.add_link(nodes["Math.001"], "Value", nodes["Mix.001"], "Fac")
        self.add_link(nodes["Group Input"], "Section3Color", nodes["Mix.001"], "Color2")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Group Input"], "Threshold2", nodes["Math.001"], "Value_001")