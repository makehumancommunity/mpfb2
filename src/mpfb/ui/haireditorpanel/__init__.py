# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025 - updated 6.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  init file for hair editor module of extension
# ------------------------------------------------------------------------------
"""This module contains functionality for haireditor."""

import os, bpy
from ...services import LogService as _LogService
_LOG = _LogService.get_logger("heireditorpanel.init")
_LOG.trace("initializing hair editor module")

from .hairproperties import HAIR_PROPERTIES, FUR_PROPERTIES
from .haireditorpanel import MPFB_PT_Hair_Editor_Panel
from .operators import *

__all__ = [
    "HAIR_PROPERTIES",
    "FUR_PROPERTIES",
    "MPFB_PT_Hair_Editor_Panel",
    "MPFB_OT_ApplyMaterial_Operator",
    "MPFB_OT_ApplyFur_Operator",
    "MPFB_OT_BakeHair_Operator",
    "MPFB_OT_GenerateHairCards_Operator",
    "MPFB_OT_RegenerateHairCards_Operator",
    "MPFB_OT_UnbakeHair_Operator",
    "MPFB_OT_DeleteHair_Operator",
    "MPFB_OT_ApplyHair_Operator"
]

