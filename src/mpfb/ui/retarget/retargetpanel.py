import os, bpy
from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import ObjectService
from ...services import SceneConfigSet
from ...services import UiService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("retarget.retargetpanel")

class MPFB_PT_RetargetOpsPanel(Abstract_Panel):
    bl_label = "Retarget"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None:
            return

        layout.operator("mpfb.suggest_retarget_mapping")
        layout.operator("mpfb.retarget")


ClassManager.add_class(MPFB_PT_RetargetOpsPanel)
