
from ....services import LogService
from ....services import BlenderConfigSet

_LOG = LogService.get_logger("standardrig.init")
_LOG.trace("initializing standard rig module")

import os, bpy

_ROOT = os.path.dirname(__file__)
_RIG_PROPERTIES_DIR = os.path.join(_ROOT, "rigproperties")
_RIG_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_RIG_PROPERTIES_DIR)

RigHelpersProperties = BlenderConfigSet(_RIG_PROPERTIES, bpy.types.Object, prefix="rh_") # pylint: disable=C0103

from .standardrigpanel import MPFB_PT_Standard_Rig_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Standard_Rig_Panel",
    "RigHelpersProperties"
    ]
