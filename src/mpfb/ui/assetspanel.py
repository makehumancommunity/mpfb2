from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("ui.assetspanel")

class MPFB_PT_Assets_Panel(Abstract_Panel):
    bl_label = "Apply assets"
    bl_category = UiService.get_value("MATERIALSCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene

ClassManager.add_class(MPFB_PT_Assets_Panel)
