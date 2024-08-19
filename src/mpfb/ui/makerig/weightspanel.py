"""File containing weights UI for makerig"""

import bpy
from mpfb import ClassManager
from ...services import LogService
from ...services import ObjectService
from ...services import UiService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("makerig.weightspanel")

class MPFB_PT_MakeRigWeights_Panel(Abstract_Panel):
    """MakeRig weights panel."""

    bl_label = "Manage weights"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_MakeRig_Panel"

    def _transfer_weights(self, context, scene, layout):
        box = self._create_box(layout, "Transfer weights", "TOOL_SETTINGS")

        armatures = ObjectService.get_selected_armature_objects()
        if len(armatures) != 2:
            box.label(text="Select 2 armatures")
            return

        if context.active_object not in armatures:
            box.label(text="Armature must be active object")
            return

        bm1 = ObjectService.find_object_of_type_amongst_nearest_relatives(armatures[0])
        bm2 = ObjectService.find_object_of_type_amongst_nearest_relatives(armatures[1])

        if bm1 is None or bm2 is None:
            box.label(text="Armature must have basemesh child")
            return

        src = context.active_object
        if src == armatures[0]:
            dst = armatures[1]
        else:
            dst = armatures[0]

        box.label(text="SRC rig: " + src.name)
        box.label(text="DST rig: " + dst.name)

        box.operator('mpfb.auto_transfer_weights')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        self._transfer_weights(context, scene, layout)

ClassManager.add_class(MPFB_PT_MakeRigWeights_Panel)


