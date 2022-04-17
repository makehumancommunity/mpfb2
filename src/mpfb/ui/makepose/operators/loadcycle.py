from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.services.animationservice import AnimationService
from mpfb.services.rigservice import RigService
from mpfb._classmanager import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("makepose.operators.loadcycle")

class MPFB_OT_Load_Walk_Cycle_Operator(bpy.types.Operator):
    """Load walk cycle from json"""
    bl_idname = "mpfb.load_walk_cycle"
    bl_label = "Load walk cycle"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        # TODO: check current mode
        return True

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        from mpfb.ui.makepose import MakePoseProperties

        #name = MakePoseProperties.get_value('name', entity_reference=context.scene)
        iterations = MakePoseProperties.get_value('iterations', entity_reference=context.scene)
        overwrite = MakePoseProperties.get_value('overwrite', entity_reference=context.scene)
        roottrans = MakePoseProperties.get_value('roottrans', entity_reference=context.scene)
        iktrans = MakePoseProperties.get_value('iktrans', entity_reference=context.scene)
        fktrans = MakePoseProperties.get_value('fktrans', entity_reference=context.scene)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        rig_type = RigService.identify_rig(armature_object)

        with open('/tmp/animation.json', 'r') as json_file:
            animation = json.load(json_file)
        _LOG.dump("Animation", animation)

        animation_bone_names = animation["animation_data"].keys()

        for bone_name in animation_bone_names:
            bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
            if not bone:
                self.report({'ERROR'}, bone_name + " is specified in the animation, but does not exist in the selected rig. Maybe you need to enable helpers? Or is it the wrong rig type?")
                return {'FINISHED'}

        AnimationService.walk_cycle_from_dict(armature_object, animation, iterations=iterations)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, "Done")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Walk_Cycle_Operator)
