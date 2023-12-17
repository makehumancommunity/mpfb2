from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb._classmanager import ClassManager
import bpy, json, math, bmesh
from mathutils import Vector, Matrix
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper
from bpy_extras.object_utils import world_to_camera_view
from ._openposeconstants import COCO

from mpfb.ui.ai.aipanel import AI_PROPERTIES

_LOG = LogService.get_logger("ai.operators.saveopenpose")
_LOG.set_level(LogService.DEBUG)


class MPFB_OT_Save_Openpose_Operator(bpy.types.Operator, ExportHelper):
    """Save pose as openpose json"""
    bl_idname = "mpfb.save_openpose"
    bl_label = "Save openpose"
    bl_options = {'REGISTER'}

    filename_ext = '.json'
    check_extension = False

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        # TODO: check current mode
        return True

    def _get_keypoints_2d(self, armature_object, bm, scene, camera, resx, resy):
        pose_keypoints_2d = []
        for position in COCO:
            keypoint = Vector([0.0, 0.0, 0.0])
            _LOG.debug("position", position)
            if position["type"] == "vertex":
                keypoint = bm.verts[position["data"]].co + armature_object.location
            if position["type"] == "mean":
                keypoint = bm.verts[position["data"][0]].co + armature_object.location
            if position["type"] in ("head", "tail"):
                bone_name = position["data"]
                loc = RigService.get_world_space_location_of_pose_bone(bone_name, armature_object)
                keypoint[0] = loc[position["type"]][0]
                keypoint[1] = loc[position["type"]][1]
                keypoint[2] = loc[position["type"]][2]

            cam_coord = world_to_camera_view(scene, camera, keypoint)
            pose_keypoints_2d.append(cam_coord[0] * resx)
            pose_keypoints_2d.append((1.0 - cam_coord[1]) * resy)
            pose_keypoints_2d.append(position["confidence"])

        _LOG.debug("pose_keypoints_2d", pose_keypoints_2d)
        return pose_keypoints_2d

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        rig_type = RigService.identify_rig(armature_object)
        if not rig_type or not "default" in rig_type:
            self.report({'ERROR'}, "Only default rig is supported")
            return {'FINISHED'}

        camera = None
        for o in bpy.context.scene.objects:
            if o.type == 'CAMERA':
                camera = o
                break

        if not camera:
            self.report({'ERROR'}, "Could not find a camera in the scene")
            return {'FINISHED'}

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        resx = context.scene.render.resolution_x
        resy = context.scene.render.resolution_y

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        for person_id in [0]:
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature_object, "Basemesh")
            if not basemesh:
                self.report({'ERROR'}, "Could not find a Basemesh object for one armature")
                return {'FINISHED'}

            depsgraph = bpy.context.evaluated_depsgraph_get()
            bm = bmesh.new()
            bm.from_object( basemesh, depsgraph )
            bm.verts.ensure_lookup_table()

            output = {
                "version": "1.3",
                "canvas_width": resx,
                "canvas_height": resy,
                "people": [
                    {
                        "person_id": person_id,
                        "pose_keypoints_2d": self._get_keypoints_2d(armature_object, bm, context.scene, camera, resx, resy),
                        "face_keypoints_2d":[],
                        "hand_left_keypoints_2d":[],
                        "hand_right_keypoints_2d":[]
                        }
                    ]}
            bm.free()
        _LOG.debug("output", output)



        with open(absolute_file_path, "w") as json_file:
            json.dump(output, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Openpose_Operator)
