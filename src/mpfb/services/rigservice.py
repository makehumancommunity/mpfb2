
import bpy
from mathutils import Matrix, Vector
from mpfb.services.logservice import LogService
from .objectservice import ObjectService
from bpy.types import PoseBone

_LOG = LogService.get_logger("services.rigservice")

_RADIAN = 0.0174532925


class RigService:

    def __init__(self):
        raise RuntimeError("You should not instance RigService. Use its static methods instead.")

    @staticmethod
    def find_pose_bone_by_name(name, armature_object):
        return armature_object.pose.bones.get(name)

    @staticmethod
    def find_edit_bone_by_name(name, armature_object):
        return armature_object.data.edit_bones.get(name)

    @staticmethod
    def activate_pose_bone_by_name(name, armature_object, also_select_bone=True, also_deselect_all_other_bones=True):
        if also_deselect_all_other_bones:
            for bone in armature_object.pose.bones:
                bone.bone.select = False
        bone = RigService.find_pose_bone_by_name(name, armature_object)
        armature_object.data.bones.active = bone.bone
        if also_select_bone:
            bone.bone.select = True
        return bone

    @staticmethod
    def remove_all_constraints_from_pose_bone(bone_name, armature_object):
        _LOG.enter()
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        _LOG.debug("bone", bone)
        for constraint in bone.constraints:
            _LOG.debug("constraint", constraint)
            bone.constraints.remove(constraint)

        bone.lock_ik_x = False
        bone.lock_ik_y = False
        bone.lock_ik_z = False

        bone.use_ik_limit_x = False
        bone.use_ik_limit_y = False
        bone.use_ik_limit_z = False

    @staticmethod
    def add_bone_constraint_to_pose_bone(bone_name, armature_object, constraint_name):
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        return bone.constraints.new(constraint_name)

    @staticmethod
    def add_copy_rotation_constraint_to_pose_bone(bone_to_restrain_name, bone_to_copy_from_name, armature_object, copy_x=True, copy_y=True, copy_z=True):
        constraint = RigService.add_bone_constraint_to_pose_bone(bone_to_restrain_name, armature_object, 'COPY_ROTATION')

        base = 'Copy '
        if copy_x:
            base = base + 'X'
        if copy_y:
            base = base + 'Y'
        if copy_z:
            base = base + 'Z'

        constraint.name = base + ' rotation'
        constraint.target = armature_object
        constraint.subtarget = bone_to_copy_from_name
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.influence = 1.0
        constraint.use_x = copy_x
        constraint.use_y = copy_y
        constraint.use_z = copy_z

        return constraint

    @staticmethod
    def add_rotation_constraint_to_pose_bone(bone_name, armature_object, limit_x=False, limit_y=False, limit_z=False):
        constraint = RigService.add_bone_constraint_to_pose_bone(bone_name, armature_object, 'LIMIT_ROTATION')
        constraint.use_transform_limit = True
        constraint.owner_space = "LOCAL"
        constraint.use_limit_x = limit_x
        constraint.use_limit_y = limit_y
        constraint.use_limit_z = limit_z
        return constraint

    @staticmethod
    def add_ik_rotation_lock_to_pose_bone(bone_name, armature_object, lock_x=False, lock_y=False, lock_z=False):
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        bone.lock_ik_x = lock_x
        bone.lock_ik_y = lock_y
        bone.lock_ik_z = lock_z
        return bone

    @staticmethod
    def add_ik_constraint_to_pose_bone(bone_name, armature_object, target, chain_length=2):
        constraint = RigService.add_bone_constraint_to_pose_bone(bone_name, armature_object, 'IK')
        if isinstance(target, PoseBone):
            constraint.target = armature_object
            constraint.subtarget = target.bone.name
        else:
            constraint.target = target
        constraint.chain_count = chain_length
        constraint.use_stretch = False
        return constraint

    @staticmethod
    def find_pose_bone_tail_world_location(bone_name, armature_object):
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        return bone.tail + armature_object.location

    @staticmethod
    def find_pose_bone_head_world_location(bone_name, armature_object):
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        return bone.head + armature_object.location

    @staticmethod
    def set_ik_rotation_limits(bone_name, armature_object, axis, min_angle=0, max_angle=0):
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        axis = str(axis).lower()
        if axis == "x":
            bone.use_ik_limit_x = True
            bone.ik_min_x = min_angle * _RADIAN
            bone.ik_max_x = max_angle * _RADIAN
        if axis == "y":
            bone.use_ik_limit_y = True
            bone.ik_min_y = min_angle * _RADIAN
            bone.ik_max_y = max_angle * _RADIAN
        if axis == "z":
            bone.use_ik_limit_z = True
            bone.ik_min_z = min_angle * _RADIAN
            bone.ik_max_z = max_angle * _RADIAN

    @staticmethod
    def get_bone_orientation_info_as_dict(armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        pose_bones = dict()
        for bone in armature_object.pose.bones:
            binfo = dict()
            binfo["head"] = bone.head.copy()
            binfo["tail"] = bone.tail.copy()
            binfo["matrix"] = bone.matrix.copy()
            pose_bones[bone.bone.name] = binfo

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        edit_bones = dict()
        for bone in armature_object.data.edit_bones:
            binfo = dict()
            binfo["head"] = bone.head.copy()
            binfo["tail"] = bone.tail.copy()
            binfo["matrix"] = bone.matrix.copy()
            binfo["roll"] = bone.roll
            binfo["length"] = bone.length
            binfo["parent"] = ""
            if bone.parent:
                binfo["parent"] = bone.parent.name
            edit_bones[bone.name] = binfo

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        out = dict()
        out["pose_bones"] = pose_bones
        out["edit_bones"] = edit_bones

        _LOG.dump("bone info", out)

        return out

    @staticmethod
    def _recurse_set_orientation(armature_object, new_bone_orientation, bone_children, bone_name):
        matrix = new_bone_orientation["pose_bones"][bone_name]["matrix"]
        _LOG.debug("matrix to apply", matrix)
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        bone.matrix = matrix.copy()

        children = bone_children[bone_name]
        for child_name in children:
            RigService._recurse_set_orientation(armature_object, new_bone_orientation, bone_children, child_name)

    @staticmethod
    def set_bone_orientation_from_info_in_dict(armature_object, new_bone_orientation):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        current_bone_orientation = RigService.get_bone_orientation_info_as_dict(armature_object)

        bone_children = dict()
        root_bones = []

        for bone_name in current_bone_orientation["edit_bones"].keys():
            _LOG.debug("Analyzing parent/child for bone", bone_name)
            if not bone_name in bone_children:
                bone_children[bone_name] = []
            bone_info = current_bone_orientation["edit_bones"][bone_name]
            if "parent" in bone_info and bone_info["parent"]:
                # Bone has a parent, so add it to parent's list of children
                parent_name = bone_info["parent"]
                if not parent_name in bone_children:
                    bone_children[parent_name] = []
                bone_children[parent_name].append(bone_name)
            else:
                # Bone does not have a parent. Assume it is a root.
                root_bones.append(bone_name)

        _LOG.dump("bone_children", bone_children.keys())
        _LOG.dump("root_bones", root_bones)

        for bone_name in root_bones:
            RigService._recurse_set_orientation(armature_object, new_bone_orientation, bone_children, bone_name)

    @staticmethod
    def _add_bone(armature, bone_info, parent_bone=None, scale=0.1):
        bone = armature.edit_bones.new(bone_info["name"])

        head = bone_info["headPos"]
        tail = bone_info["tailPos"]

        # scale = self.scaleFactor

        # Z up
        vector_head = Vector((head[0] * scale, -head[2] * scale, head[1] * scale))
        vector_tail = Vector((tail[0] * scale, -tail[2] * scale, tail[1] * scale))

        bone.head = vector_head
        bone.tail = vector_tail

        if not parent_bone is None:
            bone.parent = parent_bone

        if "matrix" in bone_info.keys():
            bone_matrix = Matrix(bone_info["matrix"])
            normalized_matrix = Matrix((bone_matrix[0], -bone_matrix[2], bone_matrix[1])).to_3x3().to_4x4()  # pylint: disable=E1136
            normalized_matrix.col[3] = bone.matrix.col[3]
            bone.matrix = normalized_matrix
        else:
            if "roll" in bone_info.keys():
                bone.roll = bone_info["roll"]

        for child in bone_info["children"]:
            RigService._add_bone(armature, child, bone, scale=scale)

    @staticmethod
    def create_rig_from_skeleton_info(name, data, parent=None, scale=0.1):

        armature = bpy.data.armatures.new(name + "Armature")
        armature_object = bpy.data.objects.new(name, armature)

        armature_object.data.display_type = 'WIRE'
        armature_object.show_in_front = True

        ObjectService.link_blender_object(armature_object, parent)

        bpy.context.view_layer.objects.active = armature_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        for bone_info in data["bones"]:
            RigService._add_bone(armature, bone_info, scale=scale)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return armature_object

    @staticmethod
    def ensure_armature_has_bone_shape_objects_as_children(armature_object):
        children = ObjectService.get_list_of_children(armature_object)
        has_circle = False
        has_sphere = False
        has_arrow = False
        prefix = armature_object.name + "."
        for child in children:
            if "bone_shape_sphere" in child.name:
                has_sphere = True
            if "bone_shape_circle" in child.name:
                has_circle = True
            if "bone_shape_arrow" in child.name:
                has_arrow = True
        if not has_circle:
            empty = ObjectService.create_empty(prefix + ".bone_shape_circle", empty_type="CIRCLE", parent=armature_object)
            empty.hide_render = True
            empty.hide_viewport = True
        if not has_sphere:
            empty = ObjectService.create_empty(prefix + ".bone_shape_sphere", empty_type="SPHERE", parent=armature_object)
            empty.hide_render = True
            empty.hide_viewport = True
        if not has_arrow:
            empty = ObjectService.create_empty(prefix + ".bone_shape_arrow", empty_type="SINGLE_ARROW", parent=armature_object)
            empty.hide_render = True
            empty.hide_viewport = True

    @staticmethod
    def display_pose_bone_as_empty(armature_object, bone_name, empty_type="SPHERE", scale=1.0):
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        RigService.ensure_armature_has_bone_shape_objects_as_children(armature_object)
        children = ObjectService.get_list_of_children(armature_object)
        expected_name = "bone_shape_sphere"
        if empty_type == "CIRCLE":
            expected_name = "bone_shape_circle"
        if empty_type == "SINGLE_ARROW":
            expected_name = "bone_shape_arrow"
        shape_object = None
        for child in children:
            if expected_name in child.name:
                shape_object = child
        if shape_object:
            bone.custom_shape = shape_object
            bone.custom_shape_scale = scale
        else:
            _LOG.warn("Was not able to find empty child")

    @staticmethod
    def get_weights(armature_object, basemesh):
        """Create a MHW-compatible weights dict"""

        # Eventhough it is unlikely we'll use these keys in MPFB, we'll assign them so that the dict
        # is compatible with the MHW format

        weights = {
            "copyright": "(c) the guy who clicked the save weights button",
            "description": "Weights for a rig",
            "license": "CC0",
            "name": "MakeHuman weights",
            "version": 110
        }

        weights["weights"] = dict()

        vertex_group_index_to_name = dict()

        for vertex_group in basemesh.vertex_groups:
            index = int(vertex_group.index)
            name = str(vertex_group.name)
            vertex_group_index_to_name[index] = name

        _LOG.dump("vertex_group_index_to_name", vertex_group_index_to_name)

        for bone in armature_object.data.bones:
            weights["weights"][str(bone.name)] = []

        _LOG.dump("Weights before vertices", weights)

        for vertex in basemesh.data.vertices:
            for group in vertex.groups:
                group_index = int(group.group)
                weight = group.weight
                if group_index in vertex_group_index_to_name:
                    name = vertex_group_index_to_name[group_index]
                    if name in weights["weights"]:
                        weights["weights"][name].append([vertex.index, weight])

        return weights

    @staticmethod
    def apply_weights(armature_object, basemesh, mhw_dict):
        weights = mhw_dict["weights"]

        for bone in armature_object.data.bones:
            if bone.name in weights:
                # Weights is array of [vertex_index, weight] pairs. Use zip to rotate it
                # so we can get an array of the values of the first column
                weight_array = weights[bone.name]
                if len(weight_array) > 0:
                    columns = list(zip(*weight_array))
                    vertex_indices = columns[0]
                else:
                    vertex_indices = []

                if not bone.name in basemesh.vertex_groups:
                    basemesh.vertex_groups.new(name=bone.name)

                vertex_group = basemesh.vertex_groups.get(bone.name)
                if len(vertex_indices) > 0:
                    vertex_group.add(vertex_indices, 1.0, 'ADD')

        vertex_group_name_to_index = dict()

        for vertex_group in basemesh.vertex_groups:
            vertex_group_name_to_index[vertex_group.name] = vertex_group.index

        for bone in armature_object.data.bones:
            if bone.name in weights and bone.name in basemesh.vertex_groups:
                for vertex_weight in weights[bone.name]:
                    vertex_index = vertex_weight[0]
                    weight = vertex_weight[1]
                    vertex = basemesh.data.vertices[vertex_index]
                    group_index = vertex_group_name_to_index[bone.name]
                    for group in vertex.groups:
                        if group.group == group_index:
                            group.weight = weight
                            break

    @staticmethod
    def identify_rig(armature_object):
        bone_name_to_rig = [
            ["oculi02.R", "toe1-1.L", "default"],
            ["oculi02.R", "default_no_toes"],
            ["thumb_01_l", "game_engine"],
            ["RThumb", "cmu_mb"],
            ["brow.T.R.002", "rigify_meta"],
            ["thumb.01_master.L", "rigify_generated"]
            ]

        for identification in bone_name_to_rig:
            if len(identification) == 3:
                if identification[0] in armature_object.data.bones and identification[1] in armature_object.data.bones:
                    return identification[2]
            else:
                if identification[0] in armature_object.data.bones:
                    return identification[1]

        return unknown
