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

_LOG = LogService.get_logger("makepose.operators.saveanimation")

class MPFB_OT_Save_Animation_Operator(bpy.types.Operator):
    """Save animation as json"""
    bl_idname = "mpfb.save_animation"
    bl_label = "Save animation"
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

        overwrite = MakePoseProperties.get_value('overwrite', entity_reference=context.scene)
        roottrans = MakePoseProperties.get_value('roottrans', entity_reference=context.scene)
        iktrans = MakePoseProperties.get_value('iktrans', entity_reference=context.scene)
        fktrans = MakePoseProperties.get_value('fktrans', entity_reference=context.scene)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        animation = AnimationService.get_key_frames_as_dict(armature_object, ik_bone_translation=iktrans, root_bone_translation=roottrans, fk_bone_translation=fktrans)
        _LOG.dump("Animation", animation)

        with open('/tmp/animation.json', 'w') as json_file:
            json.dump(animation, json_file, indent=4, sort_keys=True)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, "Done")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Animation_Operator)
