from mpfb._classmanager import ClassManager
from ..services import LogService
from ..services import UiService
from .abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("ui.createpanel")

class MPFB_PT_Create_Panel(Abstract_Panel):
    bl_label = "Create assets"
    bl_category = UiService.get_value("MODELCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene

ClassManager.add_class(MPFB_PT_Create_Panel)
