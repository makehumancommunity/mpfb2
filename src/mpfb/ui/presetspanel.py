from .. import ClassManager
from ..services import LogService
from ..services import UiService
from .abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("ui.presetspanel")

class MPFB_PT_Presets_Panel(Abstract_Panel):
    bl_label = "Manage presets"
    bl_category = UiService.get_value("MATERIALSCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene

ClassManager.add_class(MPFB_PT_Presets_Panel)
