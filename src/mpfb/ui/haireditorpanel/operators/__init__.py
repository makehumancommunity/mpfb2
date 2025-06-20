# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  init file for hair editor module operators
# ------------------------------------------------------------------------------
"""Operators for hair editor"""

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("haireditorpanel.operators")
_LOG.trace("initializing Hair editor operators")

from .setup_hair_operator import MPFB_OT_SetupHair_Operator
from .apply_hair_operator import MPFB_OT_ApplyHair_Operator
from .bake_hair_operator import MPFB_OT_BakeHair_Operator
from .generate_hair_cards_operator import MPFB_OT_GenerateHairCards_Operator
from .delete_hair_operator import MPFB_OT_DeleteHair_Operator
from .apply_fur_operator import MPFB_OT_ApplyFur_Operator
from .apply_material_operator import MPFB_OT_ApplyMaterial_Operator




__all__ = [
    "MPFB_OT_SetupHair_Operator",
    "MPFB_OT_ApplyMaterial_Operator",
    "MPFB_OT_ApplyFur_Operator",
    "MPFB_OT_ApplyHair_Operator",
    "MPFB_OT_DeleteHair_Operator",
    "MPFB_OT_BakeHair_Operator",
    "MPFB_OT_GenerateHairCards_Operator"
    ]
