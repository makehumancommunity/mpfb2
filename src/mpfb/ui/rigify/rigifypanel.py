from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
import bpy

_LOG = LogService.get_logger("ui.rigifypanel")

class MPFB_PT_Rigify_Panel(bpy.types.Panel):
    bl_label = "Convert to rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene
        layout.operator("mpfb.convert_to_rigify")

ClassManager.add_class(MPFB_PT_Rigify_Panel)
