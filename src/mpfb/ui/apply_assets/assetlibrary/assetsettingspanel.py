"""This file contains the asset settings panel."""

from .... import ClassManager
from ....services import LogService
from ....services import LocationService
from ....services import UiService
from ....services import AssetService
from ....services import SceneConfigSet
from ...abstractpanel import Abstract_Panel
import os, bpy

_LOG = LogService.get_logger("assetlibrary.assetsettingspanel")

_LOC = os.path.dirname(__file__)
ASSET_SETTINGS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
ASSET_SETTINGS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(ASSET_SETTINGS_PROPERTIES_DIR, prefix="ASLS_")

_CURRENT_SECOND_ROOT = None

ASSET_PACK_STATUS = {
    "status": None
    }

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
            "material_instances"
            ])

    def _advanced(self, scene, layout):
        box = layout.box()
        box.label(text="Advanced")
        ASSET_SETTINGS_PROPERTIES.draw_properties(scene, box, ["override_bake_check"])

    def _second_root(self, scene, layout):
        box = layout.box()
        box.label(text="Asset roots")
        ASSET_SETTINGS_PROPERTIES.draw_properties(scene, box, ["second_root"])

    def _assets(self, scene, layout):
        box = layout.box()
        box.label(text="Install assets")
        ASSET_SETTINGS_PROPERTIES.draw_properties(scene, box, ["check_zip"])
        if ASSET_PACK_STATUS["status"] is not None:
            box.label(text="FOUND ERROR:")
            if ASSET_PACK_STATUS["status"] == "MACOS":
                box.label(text="Asset pack contains MACOS")
                box.label(text="metadata, which is a strong")
                box.label(text="indication it has been")
                box.label(text="corrupted by Safari.")
                box.label(text="Switch off auto-unpacking")
                box.label(text="and/or auto-opening zips")
                box.label(text="in Safari and download")
                box.label(text="the asset pack zip again.")
            if ASSET_PACK_STATUS["status"] == "STRUCTURE":
                box.label(text="Something looking like a")
                box.label(text="pack name was found at")
                box.label(text="root level in this zip.")
                box.label(text="Was it re-packaged with")
                box.label(text="one directory level")
                box.label(text="too many?")
            if ASSET_PACK_STATUS["status"] == "NO_PACKS":
                box.label(text="There is no packs dir")
                box.label(text="at root level in this zip.")
                box.label(text="This makes it unlikely")
                box.label(text="that it is a valid")
                box.label(text="asset pack.")
            if "INVALID_ZIP" in ASSET_PACK_STATUS["status"]:
                box.label(text="Broken zip file was not")
                box.label(text="possible to open.")
            if ASSET_PACK_STATUS["status"] == "UNKNOWN":
                box.label(text="Something unforeseen was")
                box.label(text="wrong with the zip file.")
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

        self._advanced(scene, layout)

ClassManager.add_class(MPFB_PT_Asset_Settings_Panel)

