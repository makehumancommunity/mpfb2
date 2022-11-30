"""This file contains the asset settings panel."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.ui.abstractpanel import Abstract_Panel
import os

_LOG = LogService.get_logger("assetlibrary.assetsettingspanel")

_LOC = os.path.dirname(__file__)
ASSET_SETTINGS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
ASSET_SETTINGS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(ASSET_SETTINGS_PROPERTIES_DIR, prefix="ASLS_")

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

    def _draw_skin(self, scene, layout):
        box = layout.box()
        box.label(text="Skin")
        ASSET_SETTINGS_PROPERTIES.draw_properties(scene, box, [
            "skin_type",
            "material_instances"
            ])

    def _draw_eyes(self, scene, layout):
        box = layout.box()
        box.label(text="Eyes")
        ASSET_SETTINGS_PROPERTIES.draw_properties(scene, box, [
            "procedural_eyes"
            ])

    def _packs(self, scene, layout):
        box = layout.box()
        box.label(text="Asset packs")
        box.operator("mpfb.load_pack")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._draw_skin(scene, layout)
        self._draw_eyes(scene, layout)
        self._draw_mhclo(scene, layout)
        self._packs(scene, layout)


ClassManager.add_class(MPFB_PT_Asset_Settings_Panel)

