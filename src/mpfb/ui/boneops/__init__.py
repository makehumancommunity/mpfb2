import os
import bpy

from ...services import LogService
from ...services import SceneConfigSet
from ...services import BlenderConfigSet

_LOG = LogService.get_logger("boneops.init")
_LOG.trace("initializing setup boneops module")

_LOC = os.path.dirname(__file__)

_BOP_PROPERTIES_DIR = os.path.join(_LOC, "properties")
BOP_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(_BOP_PROPERTIES_DIR, prefix="BOP_")

_BONE_PROPERTIES_DIR = os.path.join(_LOC, "boneproperties")
_BONE_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_BONE_PROPERTIES_DIR)

BoneOpsBoneProperties = BlenderConfigSet(_BONE_PROPERTIES, bpy.types.Bone, lowercase_prefix=True)
BoneOpsEditBoneProperties = BlenderConfigSet(_BONE_PROPERTIES, bpy.types.EditBone, lowercase_prefix=True)

_ARM_PROPERTIES_DIR = os.path.join(_LOC, "armproperties")
_ARM_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_ARM_PROPERTIES_DIR)

BoneOpsArmatureProperties = BlenderConfigSet(_ARM_PROPERTIES, bpy.types.Armature, prefix="BOP_")

from .operators import *
from .bonestratpanel import MPFB_PT_BonestratPanel

__all__ = [
    "MPFB_PT_BonestratPanel",
    "BoneOpsArmatureProperties",
    "BoneOpsBoneProperties",
    "BoneOpsEditBoneProperties",
    ]
