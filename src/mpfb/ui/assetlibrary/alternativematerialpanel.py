"""This file contains the alternative material panel."""

from mpfb._classmanager import ClassManager
from ...services import LogService
from ...services import ObjectService
from ...services import UiService
from ...services import AssetService
from ...services import SceneConfigSet
from mpfb.ui.abstractpanel import Abstract_Panel
from mpfb.entities.objectproperties import GeneralObjectProperties
import os, bpy

_LOG = LogService.get_logger("assetlibrary.alternativematerials")

ALTMAT_PROPERTIES = SceneConfigSet([], prefix="ALTM_")

def _populate_settings(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    materials = [("DEFAULT", "Default material", "Default material", 0)]
    if not context.object:
        return materials
    asset_type = ObjectService.get_object_type(context.object)
    source = GeneralObjectProperties.get_value("asset_source", entity_reference=context.object)
    altmats = AssetService.alternative_materials_for_asset(source, str(asset_type).lower())
    altmats.sort()
    i = 1
    for mat in altmats:
        bn = str(os.path.basename(mat))
        materials.append((bn, bn.replace(".mhmat", ""), bn, i))
        i = i + 1
    _LOG.debug("materials", materials)
    return materials

_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "available_materials",
    "description": "These are the currently available materials for the selected mesh",
    "label": "Material",
    "default": 0
}
ALTMAT_PROPERTIES.add_property(_SETTINGS_LIST_PROP, _populate_settings)

class MPFB_PT_Alternative_Material_Panel(Abstract_Panel):
    """Alternative materials for selected assets."""

    bl_label = "Alternative materials"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Assets_Panel"

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if not context.object:
            layout.label(text="Select a mesh object")
            return

        asset_type = ObjectService.get_object_type(context.object)

        if not asset_type:
            layout.label(text="Only MH objects supported")
            return

        if asset_type == "Skeleton":
            layout.label(text="Select a mesh object")
            return

        if asset_type in ["Basemesh", "Proxymeshes"]:
            layout.label(text="Only clothes and bodyparts")
            layout.label(text="supported")
            return

        ALTMAT_PROPERTIES.draw_properties(scene, layout, ["available_materials"])
        layout.operator("mpfb.load_library_material")

ClassManager.add_class(MPFB_PT_Alternative_Material_Panel)

