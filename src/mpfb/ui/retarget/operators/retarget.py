'''
Ported from retarget_tool/retarget.py

@author: SWiga
'''
from ....services import LogService
from ....services import ObjectService
from .... import ClassManager
import bpy
from bpy.types import Armature
from bpy.types import Bone
import mathutils

bpy.types.Bone.target_bone = bpy.props.StringProperty(name="Bone")
bpy.types.Bone.pivot_bone = bpy.props.StringProperty(name="Bone")

_LOG = LogService.get_logger("retarget.operators.retarget")


class MPFB_OT_Retarget_Operator(bpy.types.Operator):
    """Retarget animation from active armature to first selected armature"""

    bl_idname = "mpfb.retarget"
    bl_label = "Retarget"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(context.active_object.type == 'ARMATURE')

    def execute(self, context):
        self.source_object = context.active_object
        source_armature = context.active_object.data
        target_armature = None
        animation_data = None

        for obj in context.view_layer.objects.selected:
            if obj.type == 'ARMATURE' and obj != context.active_object:
                self.target_object = obj
                animation_data = obj.animation_data_create()
                target_armature = obj.data
                break
        if not target_armature:
            print("no target armature selected")
            return {'CANCELLED'}

        target_action = bpy.data.actions.new(name="retargeted_action")
        animation_data.action = target_action
        source_animation_data = context.active_object.animation_data
        old_path = ""
        target_name = ""

        source_name = ""
        coords = []
        for fcurve in source_animation_data.action.fcurves:
            data_path = fcurve.data_path
            if data_path != old_path:
                self.copy_curve(target_action, old_path, source_name, target_name, coords)
                pos1 = data_path.find("pose.bones[") + len("pose.bones[")
                pos2 = data_path.find("]", pos1)
                source_name = data_path[pos1 + 1: pos2 - 1]
                bone = source_armature.bones[source_name]
                target_name = bone.target_bone
                print(source_name + " -> " + target_name)
                old_path = data_path
                coords = []
            coords.append(fcurve)
        return {'FINISHED'}

    def copy_curve(self, actions, data_path, source_name, target_name, coords):
        source_armature = self.source_object.data
        target_pose = self.target_object.pose
        if target_name and target_name != "":
            num_frames = len(coords[0].keyframe_points)
            target_pose.bones[target_name].rotation_mode = "QUATERNION"

            source_bone = source_armature.bones[source_name]
            target_bone = target_pose.bones[target_name].bone
            matLocal_source = source_bone.matrix_local.copy()
            matLocal_target = target_bone.matrix_local.copy()

            matWorld_source = self.source_object.matrix_world
            matWorld_target = self.target_object.matrix_world

            pose = target_pose.bones[target_name].rotation_quaternion.to_matrix().to_4x4()  #this is what is shown in the editor

            curve_type = data_path[data_path.find("].") + 2:]

            for idx in range(len(coords)):
                target_curve = actions.fcurves.new(data_path.replace(source_name, target_name), index=idx)
                target_curve.keyframe_points.add(count=num_frames)
                key_values = []
                for frame in range(num_frames):
                    if curve_type == "rotation_quaternion":
                        source_mat = mathutils.Quaternion((coords[0].evaluate(frame), coords[1].evaluate(frame), coords[2].evaluate(frame), coords[3].evaluate(frame))).to_matrix().to_4x4()
                        target_mat = matLocal_target.inverted() @ matWorld_target.inverted() @ matWorld_source @ matLocal_source @ source_mat  @ matLocal_source.inverted() @ matWorld_source.inverted()  @ matWorld_target @ matLocal_target @ pose
                        key_values.append(frame)
                        loc, rot, scale = target_mat.decompose()
                        key_values.append(rot[idx])
                        #key_values.append(target_mat.to_quaternion()[idx])
                    elif curve_type == "location":
                        source_mat = mathutils.Matrix.Translation(mathutils.Vector((coords[0].evaluate(frame), coords[1].evaluate(frame), coords[2].evaluate(frame))))
                        target_mat = matLocal_target.inverted() @ matWorld_target.inverted() @ matWorld_source @ matLocal_source @ source_mat  @ matLocal_source.inverted() @ matWorld_source.inverted()  @ matWorld_target @ matLocal_target @ pose
                        key_values.append(frame)
                        loc, rot, scale = target_mat.decompose()
                        key_values.append(loc[idx])
                    elif curve_type == "scale":
                        source_mat = mathutils.Matrix.LocRotScale(None, None, mathutils.Vector((coords[0].evaluate(frame), coords[1].evaluate(frame), coords[2].evaluate(frame))))
                        target_mat = matLocal_target.inverted() @ matWorld_target.inverted() @ matWorld_source @ matLocal_source @ source_mat  @ matLocal_source.inverted() @ matWorld_source.inverted()  @ matWorld_target @ matLocal_target @ pose
                        key_values.append(frame)
                        loc, rot, scale = target_mat.decompose()
                        key_values.append(scale[idx])

                target_curve.keyframe_points.foreach_set("co", key_values)
                target_curve.update()


ClassManager.add_class(MPFB_OT_Retarget_Operator)
