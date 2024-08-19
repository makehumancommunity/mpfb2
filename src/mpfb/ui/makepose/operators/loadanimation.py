from ....services import LogService
from ....services import LocationService
from ....services import MaterialService
from ....services import ObjectService
from ....services import AnimationService
from ....services import RigService
from mpfb._classmanager import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("makepose.operators.loadanimation")

class MPFB_OT_Load_Animation_Operator(bpy.types.Operator):
    """Load animation from json"""
    bl_idname = "mpfb.load_animation"
    bl_label = "Load animation"
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

        from ...makepose import MakePoseProperties

        #name = MakePoseProperties.get_value('name', entity_reference=context.scene)
        #pose_type = MakePoseProperties.get_value('pose_type', entity_reference=context.scene)
        overwrite = MakePoseProperties.get_value('overwrite', entity_reference=context.scene)
        roottrans = MakePoseProperties.get_value('roottrans', entity_reference=context.scene)
        iktrans = MakePoseProperties.get_value('iktrans', entity_reference=context.scene)
        fktrans = MakePoseProperties.get_value('fktrans', entity_reference=context.scene)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        with open('/tmp/animation.json', 'r') as json_file:
            animation = json.load(json_file)
        _LOG.dump("Animation", animation)

        AnimationService.set_key_frames_from_dict(armature_object, animation, ik_bone_translation=iktrans, root_bone_translation=roottrans, fk_bone_translation=fktrans)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, "Done")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Animation_Operator)
