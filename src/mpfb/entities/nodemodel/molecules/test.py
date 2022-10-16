from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.testmolecule")

class TestMolecule(Molecule):
    def __init__(self, group_name):
        _LOG.trace("Constructing Molecule for", group_name)
        Molecule.__init__(self, group_name)

    def create_group(self):
        _LOG.debug("Create group in TestMolecule")
        (input, output) = self.create_input_and_output()
        self.add_input_socket("value1")
        self.add_input_socket("value2")
        self.add_output_socket("value")

        math = self.createShaderNodeMath(operation="MULTIPLY")

        self.add_link(input, "value1", math, "Value")
        self.add_link(input, "value2", math, "Value_001")
        self.add_link(math, "Value", output, "value")

    def create_instance(self, node_tree, name=None, color=None, label=None, x=None, y=None):
        pass
