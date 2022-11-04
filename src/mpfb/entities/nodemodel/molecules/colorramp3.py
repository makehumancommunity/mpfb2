from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.colorramp3")
_GROUP_NAME = "MpfbColorRamp3"

class MpfbColorRamp3(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [557.3921508789062, 58.99164962768555]
        nodes["Group Input"].location = [-910.8173217773438, 26.482421875]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=1.000)
        self.add_input_socket("ZeroStopColor", socket_type="NodeSocketColor", default_value=[1.0, 0.0, 0.0, 1.0])
        self.add_input_socket("BetweenStep1Color", socket_type="NodeSocketColor", default_value=[0.0, 1.0, 0.0, 1.0])
        self.add_input_socket("BetweenStep2Color", socket_type="NodeSocketColor", default_value=[1.0, 0.0, 1.0, 1.0])
        self.add_input_socket("OneStopColor", socket_type="NodeSocketColor", default_value=[0.0, 0.0, 1.0, 1.0])
        self.add_input_socket("BetweenStep1Pos", socket_type="NodeSocketFloat", default_value=0.330)
        self.add_input_socket("BetweenStep2Pos", socket_type="NodeSocketFloat", default_value=0.660)

        self.add_output_socket("Color", socket_type="NodeSocketColor", default_value=[0.0, 0.0, 0.0, 0.0])

        nodes["Map Range"] = self.createShaderNodeMapRange(name="Map Range", x=-497.654, y=420.466, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Mix"] = self.createShaderNodeMixRGB(name="Mix", x=-177.693, y=331.272, Fac=0.5, Color1=[0.0, 0.0, 0.0, 1.0], Color2=[1.0, 1.0, 1.0, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)
        nodes["Map Range.001"] = self.createShaderNodeMapRange(name="Map Range.001", x=-498.586, y=46.563, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Map Range.002"] = self.createShaderNodeMapRange(name="Map Range.002", x=-499.518, y=-234.097, Value=1.000, From_Min=0.000, From_Max=1.000, To_Min=0.000, To_Max=1.000, Steps=4.000, Vector=[0.0, 0.0, 0.0], From_Min_FLOAT3=[0.0, 0.0, 0.0], From_Max_FLOAT3=[1.0, 1.0, 1.0], To_Min_FLOAT3=[0.0, 0.0, 0.0], To_Max_FLOAT3=[1.0, 1.0, 1.0], Steps_FLOAT3=[4.0, 4.0, 4.0], clamp=True, data_type='FLOAT', interpolation_type='LINEAR')
        nodes["Mix.001"] = self.createShaderNodeMixRGB(name="Mix.001", x=54.571, y=78.175, Fac=0.5, Color1=[1.0, 1.0, 1.0, 1.0], Color2=[0.0, 0.0, 0.0, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)
        nodes["Mix.002"] = self.createShaderNodeMixRGB(name="Mix.002", x=288.543, y=-127.891, Fac=0.5, Color1=[1.0, 1.0, 1.0, 1.0], Color2=[0.0, 0.0, 0.0, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)

        self.add_link(nodes["Group Input"], "Value", nodes["Map Range"], "Value")
        self.add_link(nodes["Group Input"], "BetweenStep1Pos", nodes["Map Range"], "From Max")
        self.add_link(nodes["Map Range"], "Result", nodes["Mix"], "Fac")
        self.add_link(nodes["Group Input"], "BetweenStep1Pos", nodes["Map Range.001"], "From Min")
        self.add_link(nodes["Group Input"], "Value", nodes["Map Range.001"], "Value")
        self.add_link(nodes["Map Range.001"], "Result", nodes["Mix.001"], "Fac")
        self.add_link(nodes["Group Input"], "BetweenStep2Pos", nodes["Map Range.001"], "From Max")
        self.add_link(nodes["Mix"], "Color", nodes["Mix.001"], "Color1")
        self.add_link(nodes["Group Input"], "ZeroStopColor", nodes["Mix"], "Color1")
        self.add_link(nodes["Group Input"], "BetweenStep1Color", nodes["Mix"], "Color2")
        self.add_link(nodes["Group Input"], "BetweenStep2Color", nodes["Mix.001"], "Color2")
        self.add_link(nodes["Mix.001"], "Color", nodes["Mix.002"], "Color1")
        self.add_link(nodes["Map Range.002"], "Result", nodes["Mix.002"], "Fac")
        self.add_link(nodes["Group Input"], "BetweenStep2Pos", nodes["Map Range.002"], "From Min")
        self.add_link(nodes["Group Input"], "Value", nodes["Map Range.002"], "Value")
        self.add_link(nodes["Group Input"], "OneStopColor", nodes["Mix.002"], "Color2")
        self.add_link(nodes["Mix.002"], "Color", nodes["Group Output"], "Color")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbColorRamp3(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopColor=None, BetweenStep1Color=None, BetweenStep2Color=None, OneStopColor=None, BetweenStep1Pos=None, BetweenStep2Pos=None):
#         return self._molecule_singletons["MpfbColorRamp3"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopColor=ZeroStopColor, BetweenStep1Color=BetweenStep1Color, BetweenStep2Color=BetweenStep2Color, OneStopColor=OneStopColor, BetweenStep1Pos=BetweenStep1Pos, BetweenStep2Pos=BetweenStep2Pos)


