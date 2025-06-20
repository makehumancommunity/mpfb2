# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  init file for material editor module
# ------------------------------------------------------------------------------

import os, bpy
from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("skineditorpanel.init")
_LOG.trace("initializing skin editor module")

from .skineditorpanel import MPFB_PT_Skin_Editor_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Skin_Editor_Panel",
    "MPFB_OT_CreateModularMaterial_Operator",
    "MPFB_OT_AddTattooTexture_Operator",
    "MPFB_OT_SaveTattooTexture_Operator",
    "MPFB_OT_RemoveTattooTexture_Operator",
    "MPFB_OT_AddFrecklesTexture_Operator",
    "MPFB_OT_SaveFrecklesTexture_Operator",
    "MPFB_OT_RemoveFrecklesTexture_Operator",
    "MPFB_OT_BakeMaterial_Operator",
    "MPFB_OT_UpdateMixFactor_Operator"
]
