from ....services import LogService
from ....services import LocationService
from ....services import MaterialService
from ....services import ObjectService
from ....services import AnimationService
from ....services import RigService
from .... import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("addcycle.operators.loadcycle")

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

        from ...addcycle.addcyclepanel import ADD_CYCLE_PROPERTIES

        iterations = ADD_CYCLE_PROPERTIES.get_value('iterations', entity_reference=context.scene)
        cycle = ADD_CYCLE_PROPERTIES.get_value('available_cycles', entity_reference=context.scene)

        if not cycle:
            self.report({'ERROR'}, "Must select a walk cycle")
            return {'FINISHED'}

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        rig_type = RigService.identify_rig(armature_object)

        wcdir = LocationService.get_mpfb_data("walkcycles")
        filename = os.path.join(wcdir, cycle)

        _LOG.debug("Filename", filename)

        with open(filename, 'r') as json_file:
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
