from mpfb.services.logservice import LogService
from mpfb.entities.nodemodel.molecules.molecule import Molecule
from mpfb.entities.nodemodel.molecules import MoleculeNodeManager

import bpy

_LOG = LogService.get_logger("nodemodel.cell")
_LOG.set_level(LogService.DEBUG)

class Cell(MoleculeNodeManager, Molecule):

    def __init__(self, group_name, create_duplicate=False):
        _LOG.trace("Constructing cell for", group_name)
        self.need_to_create = False
        self.group_name = group_name
        self._get_or_create_node_tree()
        MoleculeNodeManager.__init__(self, self.group)
        if self.need_to_create:
            self.create_group()
        else:
            self.update_group()