from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb._classmanager import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("developer.operators.savepose")

class MPFB_OT_Save_Pose_Operator(bpy.types.Operator):
    """Save pose as json"""
    bl_idname = "mpfb.save_pose"
    bl_label = "Save pose"
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
        name = MakePoseProperties.get_value('name', entity_reference=context.scene)
        pose_type = MakePoseProperties.get_value('pose_type', entity_reference=context.scene)
        overwrite = MakePoseProperties.get_value('overwrite', entity_reference=context.scene)
        roottrans = MakePoseProperties.get_value('roottrans', entity_reference=context.scene)
        iktrans = MakePoseProperties.get_value('iktrans', entity_reference=context.scene)
        fktrans = MakePoseProperties.get_value('fktrans', entity_reference=context.scene)
        
        if name:
            name = str(name).strip()

        if not name:
            self.report({'ERROR'}, "Must give a valid name")
            return {'FINISHED'}

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        rig_type = RigService.identify_rig(armature_object)
        if "default" in rig_type:
            rig_type = "default"

        save_pose_as = "fk"

        if pose_type == "IKFK":
            save_pose_as = "ik"
        
        onlyselected = False
           
        if pose_type == "PARTIAL":
            save_pose_as = "partial"
            onlyselected = True

        pose = RigService.get_pose_as_dict(armature_object, ik_bone_translation=iktrans, root_bone_translation=roottrans, fk_bone_translation=fktrans, onlyselected=onlyselected)
        _LOG.dump("Pose", pose)

        if pose_type == "AUTO" and pose["has_ik_bones"]:
            save_pose_as = "ik"

        poses_root = LocationService.get_user_data("poses")
        pose_root = os.path.abspath(os.path.join(poses_root, rig_type + "_" + save_pose_as))

        if not os.path.exists(pose_root):
            _LOG.debug("Will create", pose_root)
            os.makedirs(str(pose_root))

        absolute_file_path = os.path.join(pose_root, name + ".json")
        _LOG.debug("absolute_file_path", absolute_file_path)
        
        if not overwrite and os.path.exists(absolute_file_path):
            self.report({'ERROR'}, "Pose file already exists: " + absolute_file_path)
            return {'FINISHED'}

        with open(absolute_file_path, "w") as json_file:
            json.dump(pose, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Pose_Operator)
