"""This is the root panel for the asset library."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.ui.abstractpanel import Abstract_Panel
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = LogService.get_logger("ui.assetspanel")

FILTER_PROPERTIES = SceneConfigSet([{
    "type": "string",
    "name": "filter",
    "description": "Only list assets with this term in the title",
    "label": "Title must contain",
    "default": ""
    }], 'APAS_')


class MPFB_PT_Assets_Panel(Abstract_Panel):
    bl_label = "Apply assets"
    bl_category = UiService.get_value("MATERIALSCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        box = layout.box()
        box.label(text="Filter")
        FILTER_PROPERTIES.draw_properties(context.scene, box, [
            "filter"
            ])


ClassManager.add_class(MPFB_PT_Assets_Panel)
