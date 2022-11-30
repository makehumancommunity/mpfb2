from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.objectservice import ObjectService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("ui.rigpanel")

class MPFB_PT_Rig_Panel(Abstract_Panel):
    bl_label = "Rigging"
    bl_category = UiService.get_value("MODELCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            return False

        if ObjectService.object_is_basemesh_or_body_proxy(obj):
            return True

        if ObjectService.object_is_any_skeleton(obj):
            return True

        return False

ClassManager.add_class(MPFB_PT_Rig_Panel)
