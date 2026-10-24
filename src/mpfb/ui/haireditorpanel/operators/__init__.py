# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025 - updated 6.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  init file for hair editor module operators
# ------------------------------------------------------------------------------
"""Operators for hair editor"""

from ....services import LogService as _LogService
_LOG = _LogService.get_logger("haireditorpanel.operators")
_LOG.trace("initializing Hair editor operators")

from .apply_hair_operator import MPFB_OT_ApplyHair_Operator
from .toggle_section_operator import MPFB_OT_ToggleHairSection_Operator
from .toggle_bake_flag_operator import MPFB_OT_ToggleBakeFlag_Operator
from .bake_hair_operator import MPFB_OT_BakeHair_Operator
from .bake_result_operator import MPFB_OT_DismissHairBakeResult_Operator
from .generate_hair_cards_operator import MPFB_OT_GenerateHairCards_Operator
from .regenerate_hair_cards_operator import MPFB_OT_RegenerateHairCards_Operator
from .flatten_hair_alpha_operator import MPFB_OT_FlattenHairAlpha_Operator
from .unbake_hair_operator import MPFB_OT_UnbakeHair_Operator
from .reapply_overlay_operator import MPFB_OT_ReapplyFurOverlay_Operator
from .delete_hair_operator import MPFB_OT_DeleteHair_Operator
from .apply_fur_operator import MPFB_OT_ApplyFur_Operator
from .apply_material_operator import MPFB_OT_ApplyMaterial_Operator



__all__ = [
    "MPFB_OT_ApplyMaterial_Operator",
    "MPFB_OT_ApplyFur_Operator",
    "MPFB_OT_ApplyHair_Operator",
    "MPFB_OT_DeleteHair_Operator",
    "MPFB_OT_BakeHair_Operator",
    "MPFB_OT_GenerateHairCards_Operator",
    "MPFB_OT_RegenerateHairCards_Operator",
    "MPFB_OT_UnbakeHair_Operator",
    "MPFB_OT_FlattenHairAlpha_Operator",
    "MPFB_OT_ReapplyFurOverlay_Operator",
    "MPFB_OT_ToggleHairSection_Operator",
    "MPFB_OT_ToggleBakeFlag_Operator",
    "MPFB_OT_DismissHairBakeResult_Operator"
    ]
