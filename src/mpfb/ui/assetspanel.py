"""This is the root panel for the asset library."""

from mpfb._classmanager import ClassManager
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

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
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
