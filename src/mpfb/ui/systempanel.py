import bpy, sys
from mpfb._classmanager import ClassManager
from ..services import LogService
from ..services import UiService
from ..services import ObjectService
from .abstractpanel import Abstract_Panel
from mpfb import BUILD_INFO, VERSION

_LOG = LogService.get_logger("ui.systempanel")

class MPFB_PT_System_Panel(Abstract_Panel):
    bl_label = "System and resources"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")

    def _system_info(self, context, scene, layout):
        box = self._create_box(layout, "System information", "TOOL_SETTINGS")
        box.label(text="Build info: %s" % str(BUILD_INFO))
        box.label(text="Blender Version: %s" % str(bpy.app.version))
        pyver = [sys.version_info[0], sys.version_info[1], sys.version_info[2]]
        box.label(text="Python Version: %s" % str(pyver))

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._system_info(context, scene, layout)

ClassManager.add_class(MPFB_PT_System_Panel)
