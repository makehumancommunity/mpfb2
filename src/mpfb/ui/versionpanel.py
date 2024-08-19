import bpy, sys
from .. import ClassManager
from ..services import LogService
from ..services import SystemService
from ..services import LOWEST_FUNCTIONAL_BLENDER_VERSION
from .abstractpanel import Abstract_Panel
from mpfb import BUILD_INFO, VERSION

_LOG = LogService.get_logger("ui.versionpanel")

class MPFB_PT_Version_Panel(bpy.types.Panel):

    bl_label = "Too old blender"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MPFB v%d.%d-a%d" % (VERSION[0], VERSION[1], VERSION[2])

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        layout.label(text="REQUIRED BLENDER VERSION: %s" % str(LOWEST_FUNCTIONAL_BLENDER_VERSION))
        layout.label(text="")
        layout.label(text="Build info: %s" % str(BUILD_INFO))
        layout.label(text="Blender Version: %s" % str(bpy.app.version))
        pyver = [sys.version_info[0], sys.version_info[1], sys.version_info[2]]
        layout.label(text="Python Version: %s" % str(pyver))

ClassManager.add_class(MPFB_PT_Version_Panel)
