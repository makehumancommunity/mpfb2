from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.withindistanceofeither")
_GROUP_NAME = "MpfbWithinDistanceOfEither"

class MpfbWithinDistanceOfEither(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [767.79541015625, 159.26255798339844]
        nodes["Group Input"].location = [-826.2396850585938, 74.59132385253906]

        self.add_input_socket("Position", socket_type="NodeSocketVector", default_value=[0.5, 0.5, 0.0])
        self.add_input_socket("Coordinate1", socket_type="NodeSocketVector", default_value=[0.25, 0.25, 0.0])
        self.add_input_socket("Coordinate2", socket_type="NodeSocketVector", default_value=[0.75, 0.75, 0.0])
        self.add_input_socket("MaxDist", socket_type="NodeSocketFloat", default_value=0.100)

        self.add_output_socket("WithinDistance", socket_type="NodeSocketFloat", default_value=0.0)
        self.add_output_socket("ActualLeastDistance", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["WithinRange2"] = self.createShaderNodeMath(name="WithinRange2", label="WithinRange2", x=-150.688, y=-6.303, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["DistanceMultInRange1"] = self.createShaderNodeMath(name="DistanceMultInRange1", label="DistanceMultInRange1", x=101.513, y=336.261, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)
        nodes["InRangeOfEither"] = self.createShaderNodeMath(name="InRangeOfEither", label="InRangeOfEither", x=346.877, y=275.289, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=True)
        nodes["LeastDistance"] = self.createShaderNodeMath(name="LeastDistance", label="LeastDistance", x=345.329, y=84.984, Value=0.500, Value_001=0.500, Value_002=0.500, operation='ADD', use_clamp=False)
        nodes["Distance2"] = self.createShaderNodeVectorMath(name="Distance2", label="Distance2", x=-415.448, y=-144.812, Vector=[0.0, 0.0, 0.0], Vector_001=[0.0, 0.0, 0.0], Vector_002=[0.0, 0.0, 0.0], Scale=1.000, operation='DISTANCE')
        nodes["Distance1"] = self.createShaderNodeVectorMath(name="Distance1", label="Distance1", x=-435.557, y=199.147, Vector=[0.0, 0.0, 0.0], Vector_001=[0.0, 0.0, 0.0], Vector_002=[0.0, 0.0, 0.0], Scale=1.000, operation='DISTANCE')
        nodes["WithinRange1"] = self.createShaderNodeMath(name="WithinRange1", label="WithinRange1", x=-153.909, y=160.161, Value=0.500, Value_001=0.500, Value_002=0.500, operation='LESS_THAN', use_clamp=False)
        nodes["DistanceMultInRange2"] = self.createShaderNodeMath(name="DistanceMultInRange2", label="DistanceMultInRange2", x=110.739, y=-83.380, Value=0.500, Value_001=0.500, Value_002=0.500, operation='MULTIPLY', use_clamp=False)

        self.add_link(nodes["InRangeOfEither"], "Value", nodes["Group Output"], "WithinDistance")
        self.add_link(nodes["Distance2"], "Value", nodes["DistanceMultInRange2"], "Value")
        self.add_link(nodes["DistanceMultInRange1"], "Value", nodes["LeastDistance"], "Value")
        self.add_link(nodes["WithinRange1"], "Value", nodes["InRangeOfEither"], "Value")
        self.add_link(nodes["Distance1"], "Value", nodes["DistanceMultInRange1"], "Value")
        self.add_link(nodes["Group Input"], "Position", nodes["Distance1"], "Vector")
        self.add_link(nodes["Group Input"], "Position", nodes["Distance2"], "Vector")
        self.add_link(nodes["LeastDistance"], "Value", nodes["Group Output"], "ActualLeastDistance")
        self.add_link(nodes["Group Input"], "Coordinate1", nodes["Distance1"], "Vector_001")
        self.add_link(nodes["Group Input"], "Coordinate2", nodes["Distance2"], "Vector_001")
        self.add_link(nodes["Distance1"], "Value", nodes["WithinRange1"], "Value")
        self.add_link(nodes["Group Input"], "MaxDist", nodes["WithinRange1"], "Value_001")
        self.add_link(nodes["Group Input"], "MaxDist", nodes["WithinRange2"], "Value_001")
        self.add_link(nodes["Distance2"], "Value", nodes["WithinRange2"], "Value")
        self.add_link(nodes["WithinRange1"], "Value", nodes["DistanceMultInRange1"], "Value_001")
        self.add_link(nodes["WithinRange2"], "Value", nodes["DistanceMultInRange2"], "Value_001")
        self.add_link(nodes["WithinRange2"], "Value", nodes["InRangeOfEither"], "Value_001")
        self.add_link(nodes["DistanceMultInRange2"], "Value", nodes["LeastDistance"], "Value_001")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbWithinDistanceOfEither(self, x=0.0, y=0.0, name=None, label=None, Position=None, Coordinate1=None, Coordinate2=None, MaxDist=None):
#         return self._molecule_singletons["MpfbWithinDistanceOfEither"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Position=Position, Coordinate1=Coordinate1, Coordinate2=Coordinate2, MaxDist=MaxDist)
