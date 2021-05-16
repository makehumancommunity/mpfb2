from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.objectservice import ObjectService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("ui.systempanel")

class MPFB_PT_System_Panel(Abstract_Panel):
    bl_label = "System and resources"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene

ClassManager.add_class(MPFB_PT_System_Panel)
