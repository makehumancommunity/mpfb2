"""This module provides functionality for creating makehuman rigs."""

import os, bpy

from ...services import LogService
from ...services import ObjectService
from ...services import SceneConfigSet

_LOG = LogService.get_logger("makerig.init")
_LOG.trace("initializing makerig module")

_JOINT_CUBE_NAMES = []
for key in ObjectService.get_base_mesh_vertex_group_definition().keys():
    if "joint-" in key:
        _JOINT_CUBE_NAMES.append(str(key))
_JOINT_CUBE_NAMES.sort()

_JOINT_ENUM = []
_JOINT_ENUM.append(("NONE", "Don't change", "Don't change the location"))
_JOINT_ENUM.append(("CLOSEST", "To closest", "To closest joint cube"))

for name in _JOINT_CUBE_NAMES:
    _JOINT_ENUM.append((name, name, name))

def get_joints(self, context):
    return _JOINT_ENUM

_ROOT = os.path.dirname(__file__)
_MAKERIG_PROPERTIES_DIR = os.path.join(_ROOT, "properties")
_MAKERIG_PROPERTIES = SceneConfigSet.get_definitions_in_json_directory(_MAKERIG_PROPERTIES_DIR)

_HEAD_CUBE = {
    "type": "enum",
    "name": "head_cube",
    "description": "Put the bone head at the center of this joint cube",
    "label": "Move head to",
    "default": None
}

_TAIL_CUBE = {
    "type": "enum",
    "name": "tail_cube",
    "description": "Put the bone tail at the center of this joint cube",
    "label": "Move tail to",
    "default": None
}

MakeRigProperties = SceneConfigSet(_MAKERIG_PROPERTIES, prefix="MRP_") # pylint: disable=C0103
MakeRigProperties.add_property(_HEAD_CUBE, get_joints)
MakeRigProperties.add_property(_TAIL_CUBE, get_joints)

from .makerigpanel import MPFB_PT_MakeRig_Panel
from .bonespanel import MPFB_PT_MakeRigBones_Panel
from .weightspanel import MPFB_PT_MakeRigWeights_Panel
from .rigiopanel import MPFB_PT_MakeRigIO_Panel
from .operators import *

__all__ = [
    "MPFB_PT_MakeRig_Panel",
    "MPFB_PT_MakeRigBones_Panel",
    "MPFB_PT_MakeRigWeights_Panel",
    "MPFB_PT_MakeRigIO_Panel",
    "MakeRigProperties"
    ]
