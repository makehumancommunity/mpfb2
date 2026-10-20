# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         31.8.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  preparing a basemesh for hair editing, implicitly on first applied asset
# ------------------------------------------------------------------------------
from ...services.logservice import LogService
from ...services.objectservice import ObjectService
from .hairproperties import HAIR_PROPERTIES

import bpy

_LOG = LogService.get_logger("haireditorpanel.hairsetup")

_HAIR_SETUP_PROPERTY = {
    "name": "hair_setup",
    "type": "boolean",
    "description": "Hair has been initialized for this object",
    "label": "Setup hair",
    "default": False
    }

def _has_curves_child(basemesh):
    for child in ObjectService.get_list_of_children(basemesh):
        if child.type == "CURVES":
            return True
    return False

def is_hair_setup(basemesh):
    """Check if the given basemesh has already been prepared for hair editing."""
    if basemesh is None:
        return False
    if not HAIR_PROPERTIES.has_key("hair_setup", entity_reference=basemesh):
        return False
    if not HAIR_PROPERTIES.get_value("hair_setup", False, entity_reference=basemesh):
        return False
    # The flag survives save and reload, check also whether the curves are still there
    return _has_curves_child(basemesh)

def ensure_hair_setup(basemesh, context):
    """Prepare the basemesh for hair editing if that has not been done yet.

    Args:
        basemesh: The basemesh the hair is to be attached to.
        context: The blender context.

    Returns:
        bool: True if the setup was performed, False if it had already been done earlier.
    """
    _LOG.enter()
    if is_hair_setup(basemesh):
        _LOG.debug("Hair is already set up for", basemesh.name)
        return False

    ObjectService.deselect_and_deactivate_all()
    ObjectService.activate_blender_object(basemesh)

    # Add empty hair or the hair asset wont behave correctly
    bpy.ops.object.curves_empty_hair_add()

    # For eevee set curves render as strip
    if str(context.scene.render.engine).startswith("BLENDER_EEVEE"):
        context.scene.render.hair_type = 'STRIP'

    HAIR_PROPERTIES.set_value_dynamic("hair_setup", True, _HAIR_SETUP_PROPERTY, basemesh)

    ObjectService.deselect_and_deactivate_all()
    ObjectService.activate_blender_object(basemesh)

    _LOG.info("Initialized hair for basemesh", basemesh.name)
    return True
