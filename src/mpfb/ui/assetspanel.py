"""This is the root panel for the asset library."""

from .. import ClassManager
from ..services import LogService
from ..services import UiService
from ..services import AssetService
from .abstractpanel import Abstract_Panel
from ..services import SceneConfigSet

_LOG = LogService.get_logger("ui.assetspanel")

FILTER_PROPERTIES = SceneConfigSet([
    {
    "type": "string",
    "name": "filter",
    "description": "Only list assets with this term in the title",
    "label": "Title must contain",
    "default": ""
    },
    {
    "type": "string",
    "name": "packname",
    "description": "Only list assets belonging to an asset pack matching this name",
    "label": "Pack name must contain",
    "default": ""
    },
    {
    "type": "boolean",
    "name": "only_equipped",
    "description": "Only show assets which are currently equipped",
    "label": "Only equipped",
    "default": False
    }
    ], 'APAS_')


class MPFB_PT_Assets_Panel(Abstract_Panel):
    bl_label = "Apply assets"
    bl_category = UiService.get_value("MATERIALSCATEGORY")

    def system_assets(self, layout):
        (has_sys_assets, modern_sys_assets) = AssetService.check_if_modern_makehuman_system_assets_installed()
        _LOG.debug("has_sys_assets", (has_sys_assets, modern_sys_assets))

        if has_sys_assets and modern_sys_assets:
            return
        box = layout.box()
        box.label(text="NOTE ABOUT SYSTEM ASSETS")
        box.label(text="")
        if not has_sys_assets:
            box.label(text="It seems the makehuman system assets")
            box.label(text="have not been installed. You will")
            box.label(text="likely want these before trying to load")
            box.label(text="any assets")
            return
        if not modern_sys_assets:
            box.label(text="While the makehuman system assets")
            box.label(text="are installed, it seems you are using")
            box.label(text="a rather old version. You might want")
            box.label(text="to download and reinstall the latest")
            box.label(text="version of the makehuman system assets")
            box.label(text="if you encounter problems.")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout

        self.system_assets(layout)

        box = layout.box()
        box.label(text="Filter")
        show_props = ["filter"]
        if AssetService.have_any_pack_meta_data():
            _LOG.debug("There is pack metadata")
            show_props.append("packname")
        else:
            _LOG.debug("There is no pack metadata")
        show_props.append("only_equipped")
        FILTER_PROPERTIES.draw_properties(context.scene, box, show_props)


ClassManager.add_class(MPFB_PT_Assets_Panel)
