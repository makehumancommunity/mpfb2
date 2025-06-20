# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  init file for materialeditor operators
# ------------------------------------------------------------------------------

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("skineditorpanel.operators")
_LOG.trace("initializing Material operators")

from .create_modular_material import MPFB_OT_CreateModularMaterial_Operator
from .update_mix_factor_operator import MPFB_OT_UpdateMixFactor_Operator
from .add_tattoo_texture_operator import MPFB_OT_AddTattooTexture_Operator
from .save_tattoo_texture_operator import MPFB_OT_SaveTattooTexture_Operator
from .remove_tattoo_texture_operator import MPFB_OT_RemoveTattooTexture_Operator
from .add_freckles_texture_operator import MPFB_OT_AddFrecklesTexture_Operator
from .save_freckles_texture_operator import MPFB_OT_SaveFrecklesTexture_Operator
from .remove_freckles_texture_operator import MPFB_OT_RemoveFrecklesTexture_Operator
from .bake_material_operator import MPFB_OT_BakeMaterial_Operator



__all__ = [
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
