"""This file contains the asset settings panel."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.uiservice import UiService
from mpfb.services.assetservice import AssetService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.ui.abstractpanel import Abstract_Panel
import os, bpy

_LOG = LogService.get_logger("assetlibrary.assetsettingspanel")

_LOC = os.path.dirname(__file__)
ASSET_SETTINGS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
ASSET_SETTINGS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(ASSET_SETTINGS_PROPERTIES_DIR, prefix="ASLS_")

_CURRENT_SECOND_ROOT = None

class MPFB_PT_Asset_Settings_Panel(Abstract_Panel):
    """Settings for loading asset files."""

    bl_label = "Library Settings"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Assets_Panel"

    def _draw_mhclo(self, scene, layout):
        box = layout.box()
        box.label(text="Clothes, Bodyparts & Proxies")
        ASSET_SETTINGS_PROPERTIES.draw_properties(scene, box, [
            "fit_to_body",
            "mask_base_mesh",
            "delete_group",
            "specific_delete_group",
            "set_up_rigging",
            "interpolate_weights",
            "import_subrig",
            "import_weights",
            "add_subdiv_modifier",
            "subdiv_levels",
            "makeclothes_metadata"
            ])

    def _draw_materials(self, scene, layout):
        box = layout.box()
        box.label(text="Materials")
        ASSET_SETTINGS_PROPERTIES.draw_properties(scene, box, [
            "skin_type",
            "clothes_type",
            "eyes_type",
            "procedural_eyes",
            "material_instances"
            ])

    def _second_root(self, scene, layout):
        box = layout.box()
        box.label(text="Asset roots")
        ASSET_SETTINGS_PROPERTIES.draw_properties(scene, box, ["second_root"])

    def _assets(self, scene, layout):
        box = layout.box()
        box.label(text="Install assets")
        box.operator("mpfb.load_pack")
        box.operator("mpfb.install_target")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._draw_materials(scene, layout)
        self._draw_mhclo(scene, layout)
        self._assets(scene, layout)
        self._second_root(scene, layout)

        global _CURRENT_SECOND_ROOT

        if _CURRENT_SECOND_ROOT is None:
            _CURRENT_SECOND_ROOT = LocationService.get_second_root()

        sr = ASSET_SETTINGS_PROPERTIES.get_value("second_root", entity_reference=bpy.context.scene)
        if sr != _CURRENT_SECOND_ROOT:
            _LOG.debug("Second root changed", sr)
            AssetService.update_all_asset_lists()
            _CURRENT_SECOND_ROOT = sr

ClassManager.add_class(MPFB_PT_Asset_Settings_Panel)

