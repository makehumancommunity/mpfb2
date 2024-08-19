"""File containing bones UI for makerig"""

import bpy
from ... import ClassManager
from ...services import LogService
from ...services import ObjectService
from ...services import UiService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("makerig.bonespanel")

class MPFB_PT_MakeRigBones_Panel(Abstract_Panel):
    """MakeRig bones panel."""

    bl_label = "Manage bones"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_MakeRig_Panel"

    def _adjust_bone(self, context, scene, layout):
        box = self._create_box(layout, "Move head/tail", "TOOL_SETTINGS")

        basemesh = None
        armature = None

        if not context.object or context.object.type != "ARMATURE":
            box.label(text="Need armature as active")
            return

        armature = context.object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature, "Basemesh")

        if not basemesh:
            selected = ObjectService.get_selected_objects(exclude_non_mh_objects=True, exclude_armature_objects=True)
            for obj in selected:
                if ObjectService.object_is_basemesh(obj):
                    basemesh = obj

        if not basemesh:
            box.label(text="Select basemesh too")
            return

        if armature.mode != "EDIT":
            box.label(text="Edit mode only")
            return

        if len(context.selected_bones) != 1:
            box.label(text="Select exactly one bone")
            return

        props = ["head_cube", "tail_cube"]
        from ..makerig import MakeRigProperties
        MakeRigProperties.draw_properties(scene, box, props)
        box.operator('mpfb.move_bone_to_cube')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        self._adjust_bone(context, scene, layout)

ClassManager.add_class(MPFB_PT_MakeRigBones_Panel)


