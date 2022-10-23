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
        self.add_input_socket("Coordinate1", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_input_socket("Coordinate2", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_input_socket("TestCoordinate", socket_type="NodeSocketVector", default_value=[0.0, 0.0, 0.0])
        self.add_input_socket("MaxDist", socket_type="NodeSocketFloat", default_value=0.0)

        self.add_output_socket("WithinDistance", socket_type="NodeSocketFloat")
        self.add_output_socket("ActualLeastDistance", socket_type="NodeSocketFloat")

        nodes["Distance1"] = self.createShaderNodeVectorMath(name="Distance1", label="Distance1", x=-523.222900390625, y=252.5700225830078, Vector=[0.0, 0.0, 0.0], Vector_001=[0.0, 0.0, 0.0], Vector_002=[0.0, 0.0, 0.0], Scale=1.0, operation='DISTANCE')
        nodes["Distance2"] = self.createShaderNodeVectorMath(name="Distance2", label="Distance2", x=-532.3359985351562, y=-170.01158142089844, Vector=[0.0, 0.0, 0.0], Vector_001=[0.0, 0.0, 0.0], Vector_002=[0.0, 0.0, 0.0], Scale=1.0, operation='DISTANCE')
        nodes["WithinRange1"] = self.createShaderNodeMath(name="WithinRange1", label="WithinRange1", x=-244.5980987548828, y=163.18519592285156, Value=0.5, Value_001=0.5, Value_002=0.5, operation='LESS_THAN', use_clamp=False)
        nodes["WithinRange2"] = self.createShaderNodeMath(name="WithinRange2", label="WithinRange2", x=-248.4306640625, y=1.7608438730239868, Value=0.5, Value_001=0.5, Value_002=0.5, operation='LESS_THAN', use_clamp=False)
        nodes["DistanceMultInRange1"] = self.createShaderNodeMath(name="DistanceMultInRange1", label="DistanceMultInRange1", x=3.7703399658203125, y=344.3244934082031, Value=0.5, Value_001=0.5, Value_002=0.5, operation='MULTIPLY', use_clamp=False)
        nodes["DistanceMultInRange1.001"] = self.createShaderNodeMath(name="DistanceMultInRange1.001", label="DistanceMultInRange1", x=-1.9175567626953125, y=-101.42337799072266, Value=0.5, Value_001=0.5, Value_002=0.5, operation='MULTIPLY', use_clamp=False)
        nodes["InRangeOfEither"] = self.createShaderNodeMath(name="InRangeOfEither", label="InRangeOfEither", x=249.134033203125, y=283.3526306152344, Value=0.5, Value_001=0.5, Value_002=0.5, operation='ADD', use_clamp=True)
        nodes["LeastDistance"] = self.createShaderNodeMath(name="LeastDistance", label="LeastDistance", x=247.58642578125, y=93.04754638671875, Value=0.5, Value_001=0.5, Value_002=0.5, operation='ADD', use_clamp=False)

        self.add_link(nodes["InRangeOfEither"], "Value", nodes["Group Output"], "Output_4")
        self.add_link(nodes["Distance2"], "Value", nodes["DistanceMultInRange1.001"], "Value")
        self.add_link(nodes["DistanceMultInRange1"], "Value", nodes["LeastDistance"], "Value")
        self.add_link(nodes["WithinRange1"], "Value", nodes["InRangeOfEither"], "Value")
        self.add_link(nodes["Distance1"], "Value", nodes["DistanceMultInRange1"], "Value")
        self.add_link(nodes["Group Input"], "Input_2", nodes["Distance1"], "Vector")
        self.add_link(nodes["Group Input"], "Input_2", nodes["Distance2"], "Vector")
        self.add_link(nodes["LeastDistance"], "Value", nodes["Group Output"], "Output_5")
        self.add_link(nodes["Group Input"], "Input_0", nodes["Distance1"], "Vector_001")
        self.add_link(nodes["Group Input"], "Input_1", nodes["Distance2"], "Vector_001")
        self.add_link(nodes["Distance1"], "Value", nodes["WithinRange1"], "Value")
        self.add_link(nodes["Group Input"], "Input_3", nodes["WithinRange1"], "Value_001")
        self.add_link(nodes["Group Input"], "Input_3", nodes["WithinRange2"], "Value_001")
        self.add_link(nodes["Distance2"], "Value", nodes["WithinRange2"], "Value")
        self.add_link(nodes["WithinRange1"], "Value", nodes["DistanceMultInRange1"], "Value_001")
        self.add_link(nodes["WithinRange2"], "Value", nodes["DistanceMultInRange1.001"], "Value_001")
        self.add_link(nodes["WithinRange2"], "Value", nodes["InRangeOfEither"], "Value_001")
        self.add_link(nodes["DistanceMultInRange1.001"], "Value", nodes["LeastDistance"], "Value_001")
