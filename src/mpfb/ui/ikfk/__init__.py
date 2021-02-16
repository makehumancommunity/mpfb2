
from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("ikfk.init")
_LOG.trace("initializing setup ik/fk module")

import os, bpy

_ROOT = os.path.dirname(__file__)
_RIG_PROPERTIES_DIR = os.path.join(_ROOT, "rigproperties")
_RIG_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_RIG_PROPERTIES_DIR)

IkFkProperties = BlenderConfigSet(_RIG_PROPERTIES, bpy.types.Object, prefix="ikfk_") # pylint: disable=C0103

from .ikfkpanel import MPFB_PT_Ik_Fk_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Ik_Fk_Panel",
    "IkFkProperties"
    ]
