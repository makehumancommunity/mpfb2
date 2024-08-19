from mpfb.entities.objectproperties import GeneralObjectProperties
from ....services import LogService
from ....services import ObjectService
from ....services import RigService
from mpfb._classmanager import ClassManager
import bpy, json, math, bmesh
from mathutils import Vector, Matrix
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper
from bpy_extras.object_utils import world_to_camera_view
from ._openposeconstants import COCO, LEFT_HAND, RIGHT_HAND

_LOG = LogService.get_logger("ai.operators.saveopenpose")
_LOG.set_level(LogService.DEBUG)

_CREATE_DEBUG_EMPTIES = False

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
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                return True
        return False

    def _as_camera_coordinate(self, scene, camera, resx, resy, keypoint):
        # Due to limitations in world_to_camera_view(), this ends up distorted. A world coordinate is
        # not matched to what the camera actually sees in an exact manner, as the method does not take
        # all camera settings into account. The final results are unpredictable and often depressing.
        cam_coord = world_to_camera_view(scene, camera, keypoint)
        _LOG.debug("Cam projection", (keypoint, cam_coord))
        return [cam_coord[0] * resx, (1.0 - cam_coord[1]) * resy]

    def _as_xz_projection(self, scene, resx, resy, keypoint):
        from ...ai.aipanel import AI_PROPERTIES
        minx = AI_PROPERTIES.get_value("minx", entity_reference=scene)
        maxx = AI_PROPERTIES.get_value("maxx", entity_reference=scene)
        minz = AI_PROPERTIES.get_value("minz", entity_reference=scene)
        maxz = AI_PROPERTIES.get_value("maxz", entity_reference=scene)

        width = maxx - minx
        height = maxz - minz

        pctx = (keypoint[0] - minx) / width
        pctz = 1.0 - (keypoint[2] - minz) / height

        _LOG.debug("XZ projection", (width, height, keypoint[0], keypoint[2], pctx, pctz))

        return [pctx * resx, pctz * resy]

    def _get_keypoints_2d(self, armature_object, bm, scene, camera, resx, resy, mapper):

        from ...ai.aipanel import AI_PROPERTIES
        low = AI_PROPERTIES.get_value("lowconfidence", entity_reference=scene)
        medium = AI_PROPERTIES.get_value("mediumconfidence", entity_reference=scene)
        high = AI_PROPERTIES.get_value("highconfidence", entity_reference=scene)
        mode = AI_PROPERTIES.get_value("mode", entity_reference=scene)

        coord_mapping = []
        for position in mapper:
            keypoint = Vector([0.0, 0.0, 0.0])
            _LOG.debug("position", position)
            if position["type"] == "vertex":
                keypoint = armature_object.matrix_world @ bm.verts[position["data"]].co
            if position["type"] == "mean":
                keypoint = [0.0, 0.0, 0.0]
                for index in position["data"]:
                    loc = armature_object.matrix_world @ bm.verts[index].co
                    keypoint[0] += loc[0]
                    keypoint[1] += loc[1]
                    keypoint[2] += loc[2]
                keypoint[0] /= len(position["data"])
                keypoint[1] /= len(position["data"])
                keypoint[2] /= len(position["data"])
                _LOG.debug("mean", keypoint)
            if position["type"] in ("head", "tail"):
                bone_name = position["data"]
                loc = RigService.get_world_space_location_of_pose_bone(bone_name, armature_object)
                keypoint[0] = loc[position["type"]][0]
                keypoint[1] = loc[position["type"]][1]
                keypoint[2] = loc[position["type"]][2]

            if _CREATE_DEBUG_EMPTIES:
                empty = ObjectService.create_empty(position["name"])
                empty.location = keypoint
                empty.scale = Vector([0.01, 0.01, 0.01])

            remapped = [0.0, 0.0]

            if mode == "PERSP":
                remapped = self._as_camera_coordinate(scene, camera, resx, resy, keypoint)

            if mode == "XZ":
                remapped = self._as_xz_projection(scene, resx, resy, keypoint)

            coord_mapping.append(remapped[0])
            coord_mapping.append(remapped[1])

            confidence = 0.1
            if position["confidence"] == "LOW":
                confidence = low

            if position["confidence"] == "MEDIUM":
                confidence = medium

            if position["confidence"] == "HIGH":
                confidence = high

            coord_mapping.append(confidence)

        _LOG.debug("coord_mapping", (type(coord_mapping), len(coord_mapping), coord_mapping))
        return coord_mapping

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have armature(s) as selected object")
            return {'FINISHED'}

        for armature_object in context.selected_objects:

            if armature_object.type != 'ARMATURE':
                self.report({'ERROR'}, "Can only have armature(s) as selected object")
                return {'FINISHED'}

            rig_type = RigService.identify_rig(armature_object)
            if not rig_type or not "default" in rig_type:
                self.report({'ERROR'}, "Only default rig is supported")
                return {'FINISHED'}

            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature_object, "Basemesh")
            if not basemesh:
                self.report({'ERROR'}, "Could not find a basemesh for one of the armatures")
                return {'FINISHED'}

            for modifier in basemesh.modifiers:
                if modifier.type == "MASK" and modifier.vertex_group == "body" and modifier.invert_vertex_group:
                    self.report({'ERROR'}, "The base mesh has a mask modifier hiding the body. Maybe unequip a proxy?")
                    return {'FINISHED'}

        camera = None
        for o in bpy.context.scene.objects:
            if o.type == 'CAMERA':
                camera = o
                break

        if not camera:
            self.report({'ERROR'}, "Could not find a camera in the scene")
            return {'FINISHED'}

        from ...ai.aipanel import AI_PROPERTIES
        hands = AI_PROPERTIES.get_value("hands", entity_reference=context.scene)
        #face = AI_PROPERTIES.get_value("face", entity_reference=context.scene)
        mode = AI_PROPERTIES.get_value("mode", entity_reference=context.scene)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        resx = AI_PROPERTIES.get_value("resx", entity_reference=context.scene)
        resy = AI_PROPERTIES.get_value("resy", entity_reference=context.scene)

        if mode == "PERSP":
            resx = context.scene.render.resolution_x
            resy = context.scene.render.resolution_y

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        bodymapper = COCO

        output = {
            "version": "1.3",
            "canvas_width": resx,
            "canvas_height": resy,
            "people": []
            }

        person_id = 0

        for armature_object in context.selected_objects:
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature_object, "Basemesh")
            if not basemesh:
                self.report({'ERROR'}, "Could not find a Basemesh object for one armature")
                return {'FINISHED'}

            person = {
                    "person_id": person_id,
                    "pose_keypoints_2d": [],
                    "face_keypoints_2d":[],
                    "hand_left_keypoints_2d":[],
                    "hand_right_keypoints_2d":[]
                    }

            depsgraph = bpy.context.evaluated_depsgraph_get()
            bm = bmesh.new()
            bm.from_object( basemesh, depsgraph )
            bm.verts.ensure_lookup_table()

            coord_mapping = self._get_keypoints_2d(armature_object, bm, context.scene, camera, resx, resy, bodymapper)

            _LOG.debug("coord_mapping", (type(coord_mapping), len(coord_mapping), coord_mapping))

            person["pose_keypoints_2d"] = coord_mapping

            _LOG.debug("len kp2d", len(person["pose_keypoints_2d"]))

            if hands:
                person["hand_left_keypoints_2d"] = self._get_keypoints_2d(armature_object, bm, context.scene, camera, resx, resy, LEFT_HAND)
                person["hand_right_keypoints_2d"] = self._get_keypoints_2d(armature_object, bm, context.scene, camera, resx, resy, RIGHT_HAND)

            output["people"].append(person)

            bm.free()
            person_id += 1

        _LOG.debug("output", output)

        with open(absolute_file_path, "w") as json_file:
            json.dump(output, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Openpose_Operator)
