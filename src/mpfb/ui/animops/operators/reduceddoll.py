"""Functionality for creating an upload copy for mixamo."""

from ....services import LogService
from ....services import ObjectService
from ....services import RigService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
import bpy, math

_LOG = LogService.get_logger("animops.reduceddoll")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_Reduced_Doll_Operator(MpfbOperator):
    """Create a reduced copy of the character. The copy will have all clothes and body parts removed, the the helper geometry deleted and all shape keys baked"""
    bl_idname = "mpfb.reduced_doll"
    bl_label = "Mixamo reduced doll"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        MpfbOperator.__init__(self, "animops.reduceddoll")

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False
        if not ObjectService.get_object_type(context.object):
            return False
        return True

    def hardened_execute(self, context):
        _LOG.enter()

        if not context.object:
            self.report({"ERROR"}, "No object selected")
            return {'CANCELLED'}

        bm = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Basemesh")
        if not bm:
            self.report({"ERROR"}, "No basemesh found")
            return {'CANCELLED'}

        skeleton = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Skeleton")
        if not skeleton:
            self.report({"ERROR"}, "No skeleton found")
            return {'CANCELLED'}

        base_name = skeleton.name

        if bm.parent != skeleton:
            self.report({"ERROR"}, "Basemesh must have rig as parent")
            return {'CANCELLED'}

        new_skeleton = skeleton.copy()
        new_skeleton.data = skeleton.data.copy()
        new_skeleton.name = base_name + "_reduced"

        new_bm = bm.copy()
        new_bm.data = bm.data.copy()
        new_bm.name = base_name + "_body_reduced"
        new_bm.parent = new_skeleton

        for modifier in new_bm.modifiers:
            if modifier.type == 'ARMATURE':
                modifier.object = new_skeleton
            else:
                new_bm.modifiers.remove(modifier)

        ObjectService.link_blender_object(new_skeleton)
        ObjectService.link_blender_object(new_bm, parent=new_skeleton)

        ObjectService.deselect_and_deactivate_all()

        ObjectService.activate_blender_object(new_bm, context=context, deselect_all=True)

        bpy.ops.mpfb.delete_helpers()
        bpy.ops.mpfb.bake_shapekeys()

        new_skeleton.select_set(True)

        if RigService.identify_rig(new_skeleton) != "mixamo":
            self.report({"WARNING"}, "Skeleton is not a mixamo rig. This is probably not suitable for upload to Mixamo.")
        else:
            self.report({"INFO"}, "Done")

        from ...animops.animopspanel import ANIMOPS_PROPERTIES
        if ANIMOPS_PROPERTIES.get_value("call_fbx", entity_reference=context.scene):
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT', use_selection=True)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Reduced_Doll_Operator)
