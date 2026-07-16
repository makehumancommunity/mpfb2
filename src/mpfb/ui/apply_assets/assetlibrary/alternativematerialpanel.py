"""This file contains the alternative material panel."""

from .... import ClassManager
from ....services import LogService
from ....services import ObjectService
from ....services import UiService
from ....services import AssetService
from ....services import SceneConfigSet
from ...abstractpanel import Abstract_Panel
from ....entities.objectproperties import GeneralObjectProperties
import bpy, math

_LOG = LogService.get_logger("assetlibrary.alternativematerials")

ALTMAT_PROPERTIES = SceneConfigSet([
    {
    "type": "string",
    "name": "filter",
    "description": "Only list materials with this term in the name",
    "label": "Name must contain",
    "default": ""
    }
    ], prefix="ALTM_")

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

        if not context.active_object:
            layout.label(text="Select a mesh object")
            return

        asset_type = ObjectService.get_object_type(context.active_object)

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

        ALTMAT_PROPERTIES.draw_properties(scene, layout, ["filter"])

        source = GeneralObjectProperties.get_value("asset_source", entity_reference=context.active_object)
        tiles = AssetService.alternative_material_tiles_for_asset(source, str(asset_type).lower())

        current = GeneralObjectProperties.get_value("alternative_material", entity_reference=context.active_object)
        _LOG.debug("Currently applied alternative material", current)

        tot_width = bpy.context.region.width
        cols = max(1, math.floor(tot_width / 256))
        _LOG.debug("Number of UI columns to use", cols)

        grid = layout.grid_flow(columns=cols, even_columns=True, even_rows=False)

        box = grid.box()
        box.label(text="Default material")
        if not current:
            box.alert = True
        placeholder = AssetService.get_placeholder_thumbnail()
        if placeholder is not None:
            box.template_icon(icon_value=placeholder.icon_id, scale=6.0)
        operator = box.operator("mpfb.load_library_material")
        operator.restore_default = True

        filter_term = str(ALTMAT_PROPERTIES.get_value("filter", entity_reference=scene)).strip().lower()

        for tile in tiles:
            if filter_term and not filter_term in str(tile["label"]).lower():
                _LOG.trace("Tile not acceptable, does not match", (tile["label"], filter_term))
                continue

            box = grid.box()
            box.label(text=tile["label"])
            if current and current == tile["fragment"]:
                box.alert = True
            if not tile["thumb"] is None:
                box.template_icon(icon_value=tile["thumb"].icon_id, scale=6.0)
            operator = box.operator("mpfb.load_library_material")
            operator.filepath = tile["full_path"]

ClassManager.add_class(MPFB_PT_Alternative_Material_Panel)

