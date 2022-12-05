
"""This module sets up and provide global custom properties for blender objects,
for example of what type a certain object is. See JSON data under "generalproperties"
for information about the actual properties"""

import bpy, os

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("objectproperties.init")
_LOG.trace("initializing object properties module")

from mpfb.services.blenderconfigset import BlenderConfigSet

_ROOT = os.path.dirname(__file__)

_GENERAL_PROPERTIES_DIR = os.path.join(_ROOT, "generalproperties")
_GENERAL_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_GENERAL_PROPERTIES_DIR)

# This is the general properties object that can be imported
GeneralObjectProperties = BlenderConfigSet(_GENERAL_PROPERTIES, bpy.types.Object, prefix="GEN_") # pylint: disable=C0103


_HUMAN_PROPERTIES_DIR = os.path.join(_ROOT, "humanproperties")
_HUMAN_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_HUMAN_PROPERTIES_DIR)

# This is the human properties object that can be imported
HumanObjectProperties = BlenderConfigSet(_HUMAN_PROPERTIES, bpy.types.Object, prefix="HUM_") # pylint: disable=C0103


_RIG_PROPERTIES_DIR = os.path.join(_ROOT, "rigproperties")
_RIG_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_RIG_PROPERTIES_DIR)

# This is the human properties object that can be imported
SkeletonObjectProperties = BlenderConfigSet(_RIG_PROPERTIES, bpy.types.Object, prefix="SKEL_") # pylint: disable=C0103

__all__ = [
    "GeneralObjectProperties",
    "HumanObjectProperties",
    "SkeletonObjectProperties",
    ]
