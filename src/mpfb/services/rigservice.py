"""Utility functions for working with rigs, bones and weights."""

import bpy, os, fnmatch, shutil, json, re, typing
from bpy.types import PoseBone
from collections import defaultdict
from mathutils import Matrix, Vector
from .locationservice import LocationService
from .logservice import LogService
from .systemservice import SystemService
from .targetservice import TargetService
from .objectservice import ObjectService
from ..entities.objectproperties import SkeletonObjectProperties

_LOG = LogService.get_logger("services.rigservice")

_RADIAN = 0.0174532925


class RigService:
    """The RigService class is a utility class designed to provide various static methods for working with armatures, rigs, bones,
    bone contraints, poses and weights. The class is not meant to be instantiated, as all methods are static and can be called directly."""

    def __init__(self):
        """Do not instance, there are only static methods in the class"""
        raise RuntimeError("You should not instance RigService. Use its static methods instead.")

    @staticmethod
    def ensure_global_poses_are_available():
        """
        Ensures that global poses are available by copying them from the source directory to the user directory if they do not already exist.

        This method checks the source directory for pose files (JSON format) and copies them to the user directory if they are not already present.
        It creates the necessary subdirectories in the user directory if they do not exist.

        Raises:
            OSError: If there is an issue creating directories or copying files.
        """
        _LOG.enter()
        user_poses = LocationService.get_user_data("poses")
        mpfb_poses = LocationService.get_mpfb_data("poses")
        _LOG.debug("user_poses, mpfb_poses", (user_poses, mpfb_poses))
        for root, dirs, files in os.walk(mpfb_poses):
            if root != mpfb_poses:
                subdir = os.path.basename(root)
                for file in files:
                    if fnmatch.fnmatch(file, "*.json"):
                        target_dir = os.path.join(user_poses, subdir)
                        expected = os.path.join(target_dir, file)
                        existing = os.path.join(root, file)
                        if not os.path.exists(expected):
                            _LOG.debug("Pose does not exist in user dir", expected)
                            if not os.path.exists(target_dir):
                                os.makedirs(target_dir)
                            _LOG.debug("About to copy", (existing, expected))
                            shutil.copy(existing, expected)
                        else:
                            _LOG.debug("Pose already exists in user dir", expected)

    @staticmethod
    def apply_pose_as_rest_pose(armature_object):
        """This will a) apply the pose modifier on each child mesh, b) apply the current pose as rest pose on the armature_object,
        and c) create a new pose modifier on each child mesh."""
        _LOG.enter()
        for child in ObjectService.find_related_mesh_base_or_assets(armature_object, only_children=True):
            _LOG.debug("Child", child)
            ObjectService.deselect_and_deactivate_all()
            ObjectService.activate_blender_object(child)
            objtype = ObjectService.get_object_type(child)
            if objtype == "Basemesh":
                _LOG.debug("Found basemesh, will now bake its targets")
                TargetService.bake_targets(child)
            for modifier in child.modifiers:
                if modifier.type == 'ARMATURE':
                    _LOG.debug("Will apply modifier", modifier)
                    if not modifier.use_multi_modifier and modifier.object == armature_object:
                        bpy.ops.object.modifier_apply(modifier=modifier.name)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(armature_object)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.armature_apply(selected=False)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for child in ObjectService.find_related_mesh_base_or_assets(armature_object, only_children=True):
            _LOG.debug("Child", child)
            ObjectService.deselect_and_deactivate_all()
            ObjectService.activate_blender_object(child)
            RigService.ensure_armature_modifier(child, armature_object)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(armature_object)

    @staticmethod
    def ensure_armature_modifier(obj, armature_object, *, move_to_top=True, subrig=None):
        """
        Ensures that the specified object has an armature modifier linked to the given armature obj.
        If the modifier does not exist, it will be created. If it exists, it will be updated.

        This method also handles special vertex groups for preserving volume and subrigs, and ensures
        that the modifiers are ordered correctly.

        Args:
            obj (bpy.types.Object): The object to which the armature modifier should be added or updated.
            armature_object (bpy.types.Object): The armature object to be linked to the armature modifier.
            move_to_top (bool, optional): Whether to move the armature modifier to the top of the stack. Defaults to True.
            subrig (bpy.types.Object, optional): An optional subrig object to be linked to a special armature modifier. Defaults to None.

        Raises:
            RuntimeError: If there is an issue creating or updating the armature modifier.
        """
        _LOG.enter()
        vg_name = "mhmask-preserve-volume"
        sub_vg_name = "mhmask-subrig"
        index_normal = -1
        index_pv = -1
        index_sub = -1

        _LOG.trace("Position 1")

        for i, modifier in enumerate(obj.modifiers):
            if modifier.type == 'ARMATURE':
                is_subrig = modifier.vertex_group == sub_vg_name

                if is_subrig:
                    index_sub = i
                elif modifier.vertex_group == vg_name:
                    index_pv = i
                else:
                    index_normal = i

                if is_subrig:
                    if subrig is not None:
                        modifier.object = subrig
                else:
                    modifier.object = armature_object

        if not armature_object:
            _LOG.leave()
            return

        _LOG.trace("Position 2")

        if index_normal < 0:
            if index_pv >= 0:
                index_normal = index_pv
            elif index_sub >= 0:
                index_normal = index_sub
            elif move_to_top:
                index_normal = 0
            else:
                index_normal = len(obj.modifiers)

            modifier = obj.modifiers.new("Armature", 'ARMATURE')
            modifier.object = armature_object

            override = bpy.context.copy()
            override["object"] = obj
            while obj.modifiers.find(modifier.name) > index_normal:
                with bpy.context.temp_override(**override):
                    bpy.ops.object.modifier_move_up(modifier=modifier.name)

        _LOG.trace("Position 3")

        if index_pv < 0 and vg_name in obj.vertex_groups:
            index_pv = index_normal + 1

            modifier = obj.modifiers.new("Armature PV", 'ARMATURE')
            modifier.object = armature_object
            modifier.use_deform_preserve_volume = True
            modifier.use_multi_modifier = True
            modifier.vertex_group = vg_name

            if bpy.app.version_file < (3, 5, 8):  # Blender bug T103074
                modifier.invert_vertex_group = True

            override = bpy.context.copy()
            override["object"] = obj
            while obj.modifiers.find(modifier.name) > index_pv:
                with bpy.context.temp_override(**override):
                    bpy.ops.object.modifier_move_up(modifier=modifier.name)

        _LOG.trace("Position 4")

        if index_sub < 0 and subrig is not None:
            if sub_vg_name not in obj.vertex_groups:
                obj.vertex_groups.new(name=sub_vg_name)

            index_sub = max(index_normal, index_pv) + 1

            modifier = obj.modifiers.new("Armature Subrig", 'ARMATURE')
            modifier.object = subrig
            modifier.use_multi_modifier = True
            modifier.vertex_group = sub_vg_name

            if bpy.app.version_file < (3, 5, 8):  # Blender bug T103074
                modifier.invert_vertex_group = True

            while obj.modifiers.find(modifier.name) > index_sub:
                bpy.ops.object.modifier_move_up({'object': obj}, modifier=modifier.name)

        _LOG.leave()

    @staticmethod
    def get_world_space_location_of_pose_bone(bone_name, armature_object):
        """Find the head and tail of a pose bone and return their locations in world space."""
        _LOG.enter()
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)

        loc = dict()
        loc["head"] = armature_object.matrix_world @ bone.tail
        loc["tail"] = armature_object.matrix_world @ bone.head

        return loc

    @staticmethod
    def find_pose_bone_by_name(name, armature_object):
        """Find a bone with the given name of the armature object, in pose mode."""
        _LOG.enter()
        return armature_object.pose.bones.get(name)

    @staticmethod
    def find_edit_bone_by_name(name, armature_object):
        """Find a bone with the given name of the armature object, in edit mode."""
        _LOG.enter()
        return armature_object.data.edit_bones.get(name)

    @staticmethod
    def activate_pose_bone_by_name(name, armature_object, also_select_bone=True, also_deselect_all_other_bones=True):
        """Activate a bone with the given name of the armature object, in pose mode."""
        _LOG.enter()
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
        """Clear and remove all pose mode bone constraints from a bone."""
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
        """Add a pose mode constraint to a bone."""
        _LOG.enter()
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        return bone.constraints.new(constraint_name)

    @staticmethod
    def add_copy_rotation_constraint_to_pose_bone(bone_to_restrain_name, bone_to_copy_from_name, armature_object, copy_x=True, copy_y=True, copy_z=True):
        """
        Adds a Copy Rotation constraint to a pose bone, allowing it to copy the rotation of another bone.

        Args:
            bone_to_restrain_name (str): The name of the bone to which the constraint will be added.
            bone_to_copy_from_name (str): The name of the bone from which the rotation will be copied.
            armature_object (bpy.types.Object): The armature object containing the bones.
            copy_x (bool, optional): Whether to copy the rotation around the X axis. Defaults to True.
            copy_y (bool, optional): Whether to copy the rotation around the Y axis. Defaults to True.
            copy_z (bool, optional): Whether to copy the rotation around the Z axis. Defaults to True.

        Returns:
            bpy.types.Constraint: The created Copy Rotation constraint.
        """
        _LOG.enter()
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
        """
        Adds a Limit Rotation constraint to a pose bone, restricting its rotation around specified axes.

        Args:
            bone_name (str): The name of the bone to which the constraint will be added.
            armature_object (bpy.types.Object): The armature object containing the bone.
            limit_x (bool, optional): Whether to limit the rotation around the X axis. Defaults to False.
            limit_y (bool, optional): Whether to limit the rotation around the Y axis. Defaults to False.
            limit_z (bool, optional): Whether to limit the rotation around the Z axis. Defaults to False.

        Returns:
            bpy.types.Constraint: The created Limit Rotation constraint.
        """
        _LOG.enter()
        constraint = RigService.add_bone_constraint_to_pose_bone(bone_name, armature_object, 'LIMIT_ROTATION')
        constraint.use_transform_limit = True
        constraint.owner_space = "LOCAL"
        constraint.use_limit_x = limit_x
        constraint.use_limit_y = limit_y
        constraint.use_limit_z = limit_z
        return constraint

    @staticmethod
    def add_ik_rotation_lock_to_pose_bone(bone_name, armature_object, lock_x=False, lock_y=False, lock_z=False):
        """
        Adds an IK rotation lock to a pose bone, restricting its rotation around specified axes during IK solving.

        Args:
            bone_name (str): The name of the bone to which the IK rotation lock will be added.
            armature_object (bpy.types.Object): The armature object containing the bone.
            lock_x (bool, optional): Whether to lock the rotation around the X axis. Defaults to False.
            lock_y (bool, optional): Whether to lock the rotation around the Y axis. Defaults to False.
            lock_z (bool, optional): Whether to lock the rotation around the Z axis. Defaults to False.

        Returns:
            bpy.types.PoseBone: The pose bone with the added IK rotation lock.
        """
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        bone.lock_ik_x = lock_x
        bone.lock_ik_y = lock_y
        bone.lock_ik_z = lock_z
        return bone

    @staticmethod
    def add_ik_constraint_to_pose_bone(bone_name, armature_object, target, chain_length=2):
        """
        Adds an IK constraint to a pose bone, allowing it to be influenced by an IK target.

        Args:
            bone_name (str): The name of the bone to which the IK constraint will be added.
            armature_object (bpy.types.Object): The armature object containing the bone.
            target (bpy.types.Object or bpy.types.PoseBone): The target object or pose bone for the IK constraint.
            chain_length (int, optional): The number of bones in the IK chain. Defaults to 2.

        Returns:
            bpy.types.Constraint: The created IK constraint.
        """
        _LOG.enter()
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
        """
        Finds the world space location of the tail of a pose bone.

        Args:
            bone_name (str): The name of the bone.
            armature_object (bpy.types.Object): The armature object containing the bone.

        Returns:
            Vector: The world space location of the bone's tail.
        """
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        return bone.tail + armature_object.location

    @staticmethod
    def find_pose_bone_head_world_location(bone_name, armature_object):
        """
        Finds the world space location of the head of a pose bone.

        Args:
            bone_name (str): The name of the bone.
            armature_object (bpy.types.Object): The armature object containing the bone.

        Returns:
            Vector: The world space location of the bone's head.
        """
        _LOG.enter()
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        return bone.head + armature_object.location

    @staticmethod
    def set_ik_rotation_limits(bone_name, armature_object, axis, min_angle=0, max_angle=0):
        """
        Sets the IK rotation limits for a pose bone.

        Args:
            bone_name (str): The name of the bone.
            armature_object (bpy.types.Object): The armature object containing the bone.
            axis (str): The axis to set the rotation limits for ('x', 'y', or 'z').
            min_angle (float, optional): The minimum rotation angle in radians. Defaults to 0.
            max_angle (float, optional): The maximum rotation angle in radians. Defaults to 0.
        """
        _LOG.enter()
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
        """
        Retrieves the orientation information of bones in an armature object.

        This method collects the head, tail, matrix, roll, and length information of both pose bones and edit bones
        in the given armature object. It returns this information as a dictionary.

        Args:
            armature_object (bpy.types.Object): The armature object containing the bones.

        Returns:
            dict: A dictionary containing the orientation information of pose bones and edit bones.
        """
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
        _LOG.enter()
        matrix = new_bone_orientation["pose_bones"][bone_name]["matrix"]
        _LOG.debug("matrix to apply", matrix)
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        bone.matrix = matrix.copy()

        children = bone_children[bone_name]
        for child_name in children:
            RigService._recurse_set_orientation(armature_object, new_bone_orientation, bone_children, child_name)

    @staticmethod
    def set_bone_orientation_from_info_in_dict(armature_object, new_bone_orientation):
        """
        Sets the bone orientation in an armature object based on the provided orientation information.

        This method updates the orientation of bones in the given armature object using the information
        provided in the new_bone_orientation dictionary. It handles both root bones and child bones,
        ensuring the correct parent-child relationships are maintained.

        Args:
            armature_object (bpy.types.Object): The armature object containing the bones.
            new_bone_orientation (dict): A dictionary containing the new orientation information for the bones.
        """
        _LOG.enter()
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
        _LOG.enter()
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
        """
        Create a rig (armature) from the provided skeleton information.

        This method creates a new armature object based on the given skeleton information and links it to the parent object.
        It sets the armature to 'EDIT' mode and adds bones to it based on the provided data.

        Args:
            name (str): The name of the new armature.
            data (dict): A dictionary containing the skeleton information, including bone data.
            parent (bpy.types.Object, optional): The parent object to link the armature to. Defaults to None.
            scale (float, optional): The scale factor to apply to the bone positions. Defaults to 0.1.

        Returns:
            bpy.types.Object: The created armature object.
        """
        _LOG.enter()
        armature = bpy.data.armatures.new(name + "Armature")
        armature_object = bpy.data.objects.new(name, armature)

        armature_object.data.display_type = 'WIRE'
        armature_object.show_in_front = True

        ObjectService.link_blender_object(armature_object, parent)

        bpy.context.view_layer.objects.active = armature_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        for bone_info in data["bones"]:
            RigService._add_bone(armature, bone_info, scale=scale)

        RigService.normalize_rotation_mode(armature_object)

        return armature_object

    @staticmethod
    def ensure_armature_has_bone_shape_objects_as_children(armature_object):
        """
        Ensure that the armature object has bone shape objects as children.

        This method checks if the armature object has specific bone shape objects (circle, sphere, arrow) as children.
        If any of these objects are missing, it creates and hides them.

        Args:
            armature_object (bpy.types.Object): The armature object to check and add bone shape objects to.
        """
        _LOG.enter()
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
        """
        Display a pose bone as an empty object.

        This method sets a custom shape for the specified pose bone, using an empty object of the given type and scale.
        It ensures that the armature has the necessary bone shape objects as children.

        Args:
            armature_object (bpy.types.Object): The armature object containing the pose bone.
            bone_name (str): The name of the pose bone to display as an empty.
            empty_type (str, optional): The type of empty object to use ('SPHERE', 'CIRCLE', 'SINGLE_ARROW'). Defaults to 'SPHERE'.
            scale (float, optional): The scale factor to apply to the custom shape. Defaults to 1.0.
        """
        _LOG.enter()
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
            if hasattr(bone, "custom_shape_scale"):
                bone.custom_shape_scale = scale
            if hasattr(bone, "custom_shape_scale_xyz"):
                bone.custom_shape_scale_xyz = [scale, scale, scale]
        else:
            _LOG.warn("Was not able to find empty child")

    @staticmethod
    def get_weights(armature_objects, basemesh, exclude_weights_below=0.0001,
                    all_groups=False, all_bones=False, all_masks=True):
        """Create a MHW-compatible weights dict"""
        _LOG.enter()
        # Even though it is unlikely we'll use these keys in MPFB, we'll assign them so that the dict
        # is compatible with the MHW format

        weights = {
            "copyright": "(c) the guy who clicked the save weights button",
            "description": "Weights for a rig",
            "license": "CC0",
            "name": "MakeHuman weights",
            "version": 110,
            "weights": dict(),
        }

        vertex_group_index_to_name = dict()
        vertex_group_names = set()

        for vertex_group in basemesh.vertex_groups:
            index = int(vertex_group.index)
            name = str(vertex_group.name)
            vertex_group_index_to_name[index] = name
            vertex_group_names.add(name)

            # Include all groups and/or masks, depending on parameters
            if all_masks if name.startswith("mhmask-") else all_groups:
                weights["weights"][name] = []

        _LOG.dump("vertex_group_index_to_name", vertex_group_index_to_name)

        if not isinstance(armature_objects, list):
            armature_objects = [armature_objects]

        for armature_object in armature_objects:
            for bone in armature_object.data.bones:
                if all_bones and bone.use_deform or bone.name in vertex_group_names:
                    weights["weights"][str(bone.name)] = []

        _LOG.dump("Weights before vertices", weights)

        for vertex in basemesh.data.vertices:
            for group in vertex.groups:
                group_index = int(group.group)
                weight = max(0, min(1, round(group.weight, 5) + 0))
                if group_index in vertex_group_index_to_name:
                    name = vertex_group_index_to_name[group_index]
                    if name in weights["weights"]:
                        if weight >= exclude_weights_below:
                            weights["weights"][name].append([vertex.index, weight])

        return weights

    @staticmethod
    def load_weights(armature_objects, basemesh, mhw_filename, *, all=False, replace=False):
        """
        Load a json file with weights into the given mesh object.

        Args:
            armature_objects: The armature or list of armatures to use for selecting relevant groups.
            basemesh: Mesh to load weights into.
            mhw_filename: Filename to load weights from.
            all: Load all groups from the file, even if they match no bones.
            replace: Completely replace group content, i.e. vertices not mentioned in the file are removed.
        """
        _LOG.enter()
        with open(mhw_filename, 'r', encoding="utf-8") as json_file:
            weights = json.load(json_file)

        _LOG.dump("Weights", weights)

        RigService.apply_weights(armature_objects, basemesh, weights, all=all, replace=replace)

    @staticmethod
    def set_extra_bones(armature_object, extra_bones: list[str] | None):
        """
        Set extra bones for the given armature object.

        This method assigns a list of extra bones to the armature object. If the list is empty or None,
        it removes the extra bones property from the armature object.

        Args:
            armature_object (bpy.types.Object): The armature object to set extra bones for.
            extra_bones (list[str] | None): A list of extra bone names or None to remove the property.
        """
        _LOG.enter()
        id_name = SkeletonObjectProperties.get_fullname_key_from_shortname_key("extra_bones")

        if extra_bones:
            armature_object[id_name] = extra_bones
        elif id_name in armature_object:
            del armature_object[id_name]

    @staticmethod
    def get_extra_bones(armature_object) -> list[str]:
        """
        Get the list of extra bones for the given armature object.

        This method retrieves the list of extra bones assigned to the armature object.

        Args:
            armature_object (bpy.types.Object): The armature object to get extra bones from.

        Returns:
            list[str]: A list of extra bone names.
        """
        _LOG.enter()
        id_name = SkeletonObjectProperties.get_fullname_key_from_shortname_key("extra_bones")
        return armature_object.get(id_name, [])

    @staticmethod
    def get_deform_group_bones(armature_object) -> list[str]:
        """
        Get the list of deform group bones for the given armature object.

        This method retrieves the list of bones that are marked for deformation in the armature object,
        including any extra bones.

        Args:
            armature_object (bpy.types.Object): The armature object to get deform group bones from.

        Returns:
            list[str]: A list of deform group bone names.
        """
        _LOG.enter()
        bones = [bone.name for bone in armature_object.data.bones if bone.use_deform]
        bones += RigService.find_extra_bones(armature_object)
        return bones

    @staticmethod
    def find_extra_bones(armature_object) -> typing.Optional[list[str]]:
        """
        List deform bones that are not present in the rig but will be generated by Rigify.

        This method identifies deform bones that are expected to be generated by Rigify but are not
        currently present in the armature object.

        Args:
            armature_object (bpy.types.Object): The armature object to find extra bones for.

        Returns:
            typing.Optional[list[str]]: A list of extra bone names or None if no extra bones are found.
        """
        _LOG.enter()
        if generated := ObjectService.find_rigify_rig_by_metarig(armature_object):
            rig_bones = {bone.name for bone in armature_object.data.bones if bone.use_deform}
            gen_bones = {bone.name for bone in generated.data.bones if bone.use_deform}

            return sorted([
                name for name in gen_bones
                if name.startswith("DEF-") and name not in rig_bones and name[4:] not in rig_bones
            ])

        # In case of re-saving a metarig without generation, reuse the current value
        return RigService.get_extra_bones(armature_object)

    @staticmethod
    def _map_weight_groups_to_bones(armature_objects: list, group_names: typing.Iterable[str]) -> dict[str, str]:
        """Find matching bones for the given set of weight group names, with appropriate fallbacks."""
        _LOG.enter()

        def find_bone(lookup_name) -> typing.Optional[bpy.types.PoseBone]:
            # Use pose bones because they are indexed via hash table
            for obj in armature_objects:
                result_bone = obj.pose.bones.get(lookup_name, None)
                if result_bone and result_bone.bone.use_deform:
                    return result_bone

            return None

        def find_common_toe(lookup_name):
            # If trying to match a toe group, try falling back to the no-toes common toe
            if match := re.fullmatch(r'^(?:DEF-)?toe\d-\d.([LR])$', lookup_name):
                left_right = match[1]

                # Try rigify and basic versions of common toe
                result_bone = find_bone(f"toe.{left_right}") or find_bone(f"DEF-toe.{left_right}") or find_bone(f"toe1-1.{left_right}")

                # Just in case verify it has no toe children, i.e. this is truly a no-toes rig
                if result_bone and not any("toe" in child.name for child in result_bone.bone.children):
                    return result_bone

            return None

        result = {}
        extra_bones = set(name for obj in armature_objects for name in RigService.get_extra_bones(obj))

        for name in group_names:
            # Automatically switch to DEF bones when applicable.
            def_toggled_name = name[4:] if name.startswith("DEF-") else "DEF-" + name

            if pose_bone := find_bone(name) or find_bone(def_toggled_name) or find_common_toe(name):
                result[name] = pose_bone.name

            # Also include bones known to be generated later.
            elif name in extra_bones:
                result[name] = name
            elif def_toggled_name in extra_bones:
                result[name] = def_toggled_name

        return result

    @staticmethod
    def apply_weights(armature_objects, basemesh, mhw_dict, *, all=False, replace=False):
        """
        Apply weights from a given dictionary to the specified mesh object.

        This method maps weight groups to bones and assigns the weights to the corresponding vertex groups
        in the mesh object. It can optionally replace existing weights or add to them.

        Args:
            armature_objects (list[bpy.types.Object] | bpy.types.Object): The armature or list of armatures to use for selecting relevant groups.
            basemesh (bpy.types.Object): The mesh object to apply weights to.
            mhw_dict (dict): A dictionary containing weights data.
            all (bool, optional): If True, load all groups from the file, even if they match no bones. Defaults to False.
            replace (bool, optional): If True, completely replace group content, i.e., vertices not mentioned in the file are removed. Defaults to False.
        """
        _LOG.enter()
        weights = mhw_dict["weights"]

        # Map bones to groups
        if not isinstance(armature_objects, list):
            armature_objects = [armature_objects]

        group_to_bone = RigService._map_weight_groups_to_bones(armature_objects, weights.keys())

        bone_to_groups = defaultdict(list)
        for name, bone_name in group_to_bone.items():
            bone_to_groups[bone_name].append(name)

        # Compute list and order of groups to import, using topology order of bones
        bone_names = [name
                      for arm in armature_objects
                      for name in ([bone.name for bone in arm.data.bones if bone.use_deform]
                                   +RigService.get_extra_bones(arm))]
        names = [name for bone in dict.fromkeys(bone_names) for name in bone_to_groups[bone]]

        assert len(names) == len(group_to_bone)

        # Add masks and other groups
        names += [name for name in weights.keys()
                  if name not in group_to_bone
                  and (all or name.startswith("mhmask-"))]

        # Clear vertex groups
        remove_indices = list(range(len(basemesh.data.vertices))) if replace else []

        for group_name in names:
            bone_name = group_to_bone.get(group_name, group_name)
            vertex_group = basemesh.vertex_groups.get(bone_name)

            if vertex_group:
                if replace:
                    # Remove all vertices
                    vertex_group.remove(remove_indices)

                elif weight_array := weights[group_name]:
                    # Clear specific vertices
                    vertex_indices, vertex_weights = zip(*weight_array)  # pylint: disable=W0612
                    vertex_group.add(vertex_indices, 0.0, 'REPLACE')

        # Assign group weights: allows combining groups by adding duplicate vertex entries together
        for group_name in names:
            weight_array = weights[group_name]

            if all or weight_array:
                bone_name = group_to_bone.get(group_name, group_name)
                vertex_group = basemesh.vertex_groups.get(bone_name)

                if not vertex_group:
                    vertex_group = basemesh.vertex_groups.new(name=bone_name)

                for vertex_index, weight in weight_array:
                    vertex_group.add([vertex_index], weight, 'ADD')

    @staticmethod
    def identify_rig(armature_object):
        """
        Identify the rig type of the given armature object.

        This method attempts to determine the rig type based on the presence of specific bone names
        in the armature object. It uses a predefined list of bone names associated with different rig types.

        Args:
            armature_object (bpy.types.Object): The armature object to identify the rig type for.

        Returns:
            str: The identified rig type.
        """
        _LOG.enter()
        bone_name_to_rig = [
            ["oculi02.R", "default_no_toes"],
            ["oculi02.R", "toe2-1.L", "default"],
            ["thumb_01_l", "game_engine"],
            ["thumb_01_l", "breast_l", "game_engine_with_breast"],
            ["RThumb", "cmu_mb"],
            ["mixamo:Hips", "mixamo"],
            ["mixamorig:LeftHandThumb1", "mixamorig:LeftBreast", "mixamo_extended"],
            ["brow.T.R.002", "rigify.human"],
            ["brow.T.R.002", "toe2-1.L", "rigify.human_toes"],
            ["ORG-clavicle_l", "rigify_generated.game_engine"],
            ["ORG-brow.T.R.002", "rigify_generated.human"],
            ["ORG-brow.T.R.002", "ORG-toe2-1.L", "rigify_generated.human_toes"]
            ]

        guessed_rig = None

        for identification in bone_name_to_rig:
            _LOG.debug("Matching identification", identification)
            if len(identification) == 3:
                if identification[0] in armature_object.data.bones and identification[1] in armature_object.data.bones:
                    _LOG.debug("Matched two")
                    guessed_rig = identification[2]
            else:
                if identification[0] in armature_object.data.bones:
                    _LOG.debug("Matched one")
                    guessed_rig = identification[1]
            _LOG.debug("Guessed rig is now", guessed_rig)

        if guessed_rig is None:
            if ObjectService.object_is_generated_rigify_rig(armature_object):
                guessed_rig = "rigify_generated.unknown"
            elif ObjectService.object_is_rigify_metarig(armature_object, check_bones=True):
                guessed_rig = "rigify.unknown"
            else:
                guessed_rig = "unknown"

        if guessed_rig == "unknown":
            for bone in armature_object.data.bones:
                if "mixamo" in bone.name:
                    guessed_rig = "mixamo"
                    break

        return guessed_rig

    @staticmethod
    def get_rig_weight_fallbacks(rig_type):
        """
        Get a list of rig types to try loading weights for in order.

        This method returns a list of rig types that should be tried in sequence when loading weights,
        based on the provided rig type. It uses a predefined fallback table to determine the order.

        Args:
            rig_type (str): The initial rig type to get fallbacks for.

        Returns:
            list[str]: A list of rig types to try loading weights for in order.
        """
        _LOG.enter()
        fallback_table = {
            # Estimate no-toes from the toes version
            "default_no_toes": ["default"],
            # Rigify toes version retains the common toe control, so go both ways
            "rigify.human": ["rigify.human_toes"],
            "rigify.human_toes": ["rigify.human"],
        }

        return [rig_type, *fallback_table.get(rig_type, [])]

    @staticmethod
    def mirror_bone_weights_to_other_side_bone(armature_object, source_bone_name, target_bone_name):
        """
        Mirror bone weights from one side bone to the other side bone.

        This method mirrors the weights of the source bone to the target bone within the given armature object.

        Args:
            armature_object (bpy.types.Object): The armature object containing the bones.
            source_bone_name (str): The name of the source bone to mirror weights from.
            target_bone_name (str): The name of the target bone to mirror weights to.
        """
        _LOG.enter()
        _LOG.debug("Will mirror side-to-side", (source_bone_name, target_bone_name))

    @staticmethod
    def mirror_bone_weights_inside_center_bone(armature_object, bone_name, left_to_right=False):
        """
        Mirror bone weights internally within a center bone.

        This method mirrors the weights within a center bone, either from left to right or right to left,
        within the given armature object.

        Args:
            armature_object (bpy.types.Object): The armature object containing the bone.
            bone_name (str): The name of the center bone to mirror weights within.
            left_to_right (bool, optional): If True, mirror weights from left to right. Defaults to False.
        """
        _LOG.enter()
        _LOG.debug("Will mirror internally", (bone_name, left_to_right))

    @staticmethod
    def symmetrize_all_bone_weights(armature_object, left_to_right=False, rig_type=None):
        """
        Symmetrize all bone weights in the armature object.

        This method mirrors the weights of bones from one side to the other within the given armature object.
        It identifies the source and destination terms based on the rig type and the direction specified.

        Args:
            armature_object (bpy.types.Object): The armature object containing the bones.
            left_to_right (bool, optional): If True, mirror weights from left to right. Defaults to False.
            rig_type (str, optional): The type of rig to use for identifying source and destination terms. Defaults to None.
        """
        _LOG.enter()
        source_terms = {
            True: {
                "default": ".L"
                },
            False: {
                "default": ".R"
                }
            }
        if not rig_type:
            rig_type = RigService.identify_rig(armature_object)
        if not rig_type or rig_type == "unknown":
            rig_type = "default"
        source_term = source_terms[left_to_right][rig_type]
        destination_term = source_terms[not left_to_right][rig_type]

        for bone in armature_object.data.bones:
            if str(bone.name).lower().endswith(str(source_term).lower()):
                _LOG.debug("Source side bone", bone.name)
                neutral_name = str(bone.name)[0:len(bone.name) - len(source_term)]
                destination_name = neutral_name + destination_term
                RigService.mirror_bone_weights_to_other_side_bone(armature_object, str(bone.name), destination_name)
            else:
                if str(bone.name).lower().endswith(str(destination_term).lower()):
                    _LOG.debug("Destination side bone", bone.name)
                else:
                    _LOG.debug("Center bone", bone.name)
                    RigService.mirror_bone_weights_inside_center_bone(armature_object, str(bone.name), left_to_right)

    @staticmethod
    def set_pose_from_dict(armature_object, pose, from_rest_pose=True):
        """
        Set the pose of an armature object from a dictionary.

        This method sets the pose of the given armature object based on the provided pose dictionary.
        It can optionally start from the rest pose.

        Args:
            armature_object (bpy.types.Object): The armature object to set the pose for.
            pose (dict): A dictionary containing bone rotations and translations.
            from_rest_pose (bool, optional): If True, start from the rest pose. Defaults to True.
        """
        _LOG.enter()
        if from_rest_pose:
            bpy.ops.pose.select_all(action="SELECT")
        else:
            bpy.ops.pose.select_all(action="DESELECT")
            for bone_name in pose["bone_rotations"].keys():
                bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
                if bone:
                    bone.bone.select = True
            for bone_name in pose["bone_translations"].keys():
                bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
                if bone:
                    bone.bone.select = True
        bpy.ops.pose.transforms_clear()
        bpy.ops.pose.select_all(action="DESELECT")

        trans_factor_x = 1
        trans_factor_y = 1
        trans_factor_z = 1

        if "default" in pose["skeleton_type"]:
            bottom = RigService.find_pose_bone_by_name("spine05", armature_object).head
            top = RigService.find_pose_bone_by_name("spine01", armature_object).tail
            left = RigService.find_pose_bone_by_name("shoulder01.L", armature_object).tail
            right = RigService.find_pose_bone_by_name("shoulder01.R", armature_object).tail

            spine_length = abs((top - bottom).length)
            shoulder_width = abs((left - right).length)

            if "original_spine_length" in pose and pose["original_spine_length"] > 0.0001:
                trans_factor_z = spine_length / pose["original_spine_length"]

            if "original_shoulder_width" in pose and pose["original_shoulder_width"] > 0.0001:
                trans_factor_x = trans_factor_y = shoulder_width / pose["original_shoulder_width"]

        for name in pose["bone_translations"]:
            bone = RigService.find_pose_bone_by_name(name, armature_object)
            if bone:
                trans = [0, 0, 0]
                trans[0] = pose["bone_translations"][name][0] * trans_factor_x
                trans[1] = pose["bone_translations"][name][1] * trans_factor_y
                trans[2] = pose["bone_translations"][name][2] * trans_factor_z
                bone.location = bone.location + Vector(trans)
        for name in pose["bone_rotations"]:
            bone = RigService.find_pose_bone_by_name(name, armature_object)
            if bone:
                bone.rotation_euler = pose["bone_rotations"][name]

    @staticmethod
    def get_pose_as_dict(armature_object, root_bone_translation=True, ik_bone_translation=True, fk_bone_translation=False, onlyselected=False):
        """
        Get the current pose of an armature object as a dictionary.

        This method retrieves the current pose of the given armature object and returns it as a dictionary.
        It includes options to include root bone translation, IK bone translation, FK bone translation, and only selected bones.

        Args:
            armature_object (bpy.types.Object): The armature object to get the pose from.
            root_bone_translation (bool, optional): If True, include root bone translation. Defaults to True.
            ik_bone_translation (bool, optional): If True, include IK bone translation. Defaults to True.
            fk_bone_translation (bool, optional): If True, include FK bone translation. Defaults to False.
            onlyselected (bool, optional): If True, include only selected bones. Defaults to False.

        Returns:
            dict: A dictionary containing the current pose of the armature object.
        """
        _LOG.enter()
        pose = dict()
        pose["skeleton_type"] = RigService.identify_rig(armature_object)

        ik_terms = []
        root_bone_name = ""
        spine_length = 0
        shoulder_width = 0

        if "default" in pose["skeleton_type"]:
            ik_terms.append("_grip")
            ik_terms.append("_ik")
            root_bone_name = "root"
            bottom = RigService.find_pose_bone_by_name("spine05", armature_object).head
            top = RigService.find_pose_bone_by_name("spine01", armature_object).tail

            left = RigService.find_pose_bone_by_name("shoulder01.L", armature_object).tail
            right = RigService.find_pose_bone_by_name("shoulder01.R", armature_object).tail

            spine_length = abs((top - bottom).length)
            shoulder_width = abs((left - right).length)

        pose["original_spine_length"] = spine_length
        pose["original_shoulder_width"] = shoulder_width

        pose["bone_rotations"] = dict()
        pose["bone_translations"] = dict()
        pose["has_ik_bones"] = False

        _LOG.debug("onlyselected", onlyselected)

        for bone in bpy.context.selected_pose_bones_from_active_object:
            _LOG.debug("bone in selected", bone)

        for bone in armature_object.pose.bones:
            euler = bone.rotation_euler
            x = abs(euler[0])
            y = abs(euler[1])
            z = abs(euler[2])

            if not onlyselected or bone in bpy.context.selected_pose_bones:
                if x > 0.0001 or y > 0.0001 or z > 0.0001:
                    pose["bone_rotations"][bone.name] = [euler[0], euler[1], euler[2]]

            is_ik = False
            for term in ik_terms:
                if str(bone.name).endswith(term):
                    is_ik = True
                    pose["has_ik_bones"] = True

            matrix = None
            if is_ik and ik_bone_translation:
                matrix = bone.matrix_basis

            if bone.name == root_bone_name and root_bone_translation:
                matrix = bone.matrix_basis

            if bone.name != root_bone_name and not is_ik and fk_bone_translation:
                # Assume this is a FK bone
                matrix = bone.matrix_basis

            if onlyselected:
                if not bone in bpy.context.selected_pose_bones:
                    matrix = None

            if matrix:
                _LOG.debug("matrix", matrix)
                (trans, loc, scale) = matrix.decompose()  # pylint: disable=W0612
                _LOG.debug("trans", trans)

                x = abs(trans[0])
                y = abs(trans[1])
                z = abs(trans[2])

                if x > 0.0001 or y > 0.0001 or z > 0.0001:
                    pose["bone_translations"][bone.name] = [ trans[0], trans[1], trans[2] ]

        return pose

    @staticmethod
    def refit_existing_armature(armature_object, basemesh):
        """
        Refit an existing armature to a new basemesh.

        This method attempts to refit the given armature object to the provided basemesh. If the armature is a Rigify metarig,
        it will refit the metarig and regenerate the rig. The method identifies the rig type and uses the appropriate rig file
        for refitting.

        Args:
            armature_object (bpy.types.Object): The armature object to be refitted.
            basemesh (bpy.types.Object): The new basemesh to fit the armature to.

        Raises:
            ValueError: If the rig type cannot be identified or if the rig is a generated Rigify rig.
        """
        _LOG.enter()
        _LOG.debug("Armature object", armature_object)

        # Try to refit Rigify metarig instead and re-generate
        if metarig := ObjectService.find_rigify_metarig_by_rig(armature_object):
            RigService.refit_existing_armature(metarig, basemesh)
            return

        rig_type = RigService.identify_rig(armature_object)

        _LOG.debug("Rig type", rig_type)

        if not rig_type:
            raise ValueError("Could not identify rig")

        if "generated" in rig_type:
            raise ValueError("Cannot refit a generated rigify rig")

        rigdir = LocationService.get_mpfb_data("rigs")

        if rig_type.startswith("rigify."):
            rigdir = os.path.join(rigdir, "rigify")
            rig_type = rig_type[7:]
        else:
            rigdir = os.path.join(rigdir, "standard")

        rig_file = os.path.join(rigdir, "rig." + rig_type + ".json")

        RigService._do_refit_existing_armature(armature_object, basemesh, rig_file)

    @staticmethod
    def refit_existing_subrig(armature_object, parent_rig):
        """
        Refit an existing subrig to a new parent rig.

        This method attempts to refit the given subrig armature object to the provided parent rig. It identifies the asset mesh
        associated with the subrig and uses the appropriate rig file for refitting.

        Args:
            armature_object (bpy.types.Object): The subrig armature object to be refitted.
            parent_rig (bpy.types.Object): The parent rig to fit the subrig to.

        Raises:
            ValueError: If the subrig asset mesh or asset file cannot be found.
        """
        _LOG.enter()
        from ..entities.objectproperties import GeneralObjectProperties

        assert not ObjectService.object_is_generated_rigify_rig(armature_object)

        children = list(ObjectService.find_deformed_child_meshes(armature_object))

        if generated := ObjectService.find_rigify_rig_by_metarig(armature_object):
            children += list(ObjectService.find_deformed_child_meshes(generated))

        uuid = GeneralObjectProperties.get_value("uuid", entity_reference=armature_object)
        asset_mesh = None

        for child in children:
            if not ObjectService.object_is_any_mesh_asset(child):
                continue

            if uuid and uuid != GeneralObjectProperties.get_value("uuid", entity_reference=child):
                continue

            asset_mesh = child
            break
        else:
            raise ValueError("Could not find subrig asset mesh")

        from .clothesservice import ClothesService  # To avoid a circular import

        asset_file = ClothesService.find_clothes_absolute_path(asset_mesh)

        if not asset_file:
            raise ValueError("Could not find subrig asset file")

        rig_file = os.path.splitext(asset_file)[0] + ".mpfbskel"

        RigService._do_refit_existing_armature(armature_object, asset_mesh, rig_file, parent_rig)

    @staticmethod
    def _do_refit_existing_armature(armature_object, basemesh, rig_file, parent_rig=None):
        _LOG.enter()
        from ..entities.rig import Rig
        _LOG.reset_timer()

        current_active_object = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = armature_object

        _LOG.debug("Rig file", rig_file)

        rig = Rig.from_json_file_and_basemesh(rig_file, basemesh, parent=parent_rig)
        rig.armature_object = armature_object

        rig.reposition_edit_bone()

        # Automatically re-generate Rigify metarigs
        if ObjectService.find_rigify_rig_by_metarig(armature_object):
            if SystemService.check_for_rigify():
                bpy.ops.pose.rigify_generate()

        bpy.context.view_layer.objects.active = current_active_object
        _LOG.time("Refitting took")

    @staticmethod
    def normalize_rotation_mode(armature_object, rotation_mode="XYZ"):
        """
        Normalize the rotation mode of all bones in an armature object.

        This method sets the rotation mode of all bones in the given armature object to the specified rotation mode.

        Args:
            armature_object (bpy.types.Object): The armature object containing the bones.
            rotation_mode (str, optional): The rotation mode to set for all bones. Defaults to "XYZ".
        """
        _LOG.enter()
        bpy.context.view_layer.objects.active = armature_object
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for bone in armature_object.pose.bones:
            bone.rotation_mode = rotation_mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    @staticmethod
    def find_leg_length(armature_object):
        """
        Find the total length of the leg bones in an armature object.

        This method calculates the total length of the leg bones in the given armature object. It is currently implemented
        only for the default rig type.

        Args:
            armature_object (bpy.types.Object): The armature object containing the leg bones.

        Returns:
            float: The total length of the leg bones.

        Raises:
            ValueError: If the rig type is not the default rig or if any of the leg bones cannot be found.
        """
        _LOG.enter()
        rig_type = RigService.identify_rig(armature_object)
        if not "default" in rig_type:
            raise ValueError('find_leg_length is only implemented for the default rig so far')

        right_leg = ["upperleg01.R", "upperleg02.R", "lowerleg01.R", "lowerleg02.R"]

        leg_length = 0.0
        for bone_name in right_leg:
            bone = armature_object.data.bones.get(bone_name)
            if not bone:
                raise ValueError('Could not find bone ' + bone_name)
            leg_length = leg_length + bone.length

        return leg_length

    @staticmethod
    def find_arm_length(armature_object):
        """
        Find the total length of the arm bones in an armature object.

        This method calculates the total length of the arm bones in the given armature object. It is currently implemented
        only for the default rig type.

        Args:
            armature_object (bpy.types.Object): The armature object containing the arm bones.

        Returns:
            float: The total length of the arm bones.

        Raises:
            ValueError: If the rig type is not the default rig or if any of the arm bones cannot be found.
        """
        _LOG.enter()
        rig_type = RigService.identify_rig(armature_object)
        if not "default" in rig_type:
            raise ValueError('find_arm_length is only implemented for the default rig so far')

        right_arm = ["upperarm01.R", "upperarm02.R", "lowerarm01.R", "lowerarm02.R"]

        arm_length = 0.0
        for bone_name in right_arm:
            bone = armature_object.data.bones.get(bone_name)
            if not bone:
                raise ValueError('Could not find bone ' + bone_name)
            arm_length = arm_length + bone.length

        return arm_length

    @staticmethod
    def copy_pose(from_armature, to_armature, only_rotation=True):
        """
        Copy the pose from one armature to another.

        This method copies the pose (rotations, translations, and scalings) from the source armature to the target armature.
        By default, it only copies the rotations, but it can also copy translations and scalings if specified.

        Args:
            from_armature (bpy.types.Object): The source armature object to copy the pose from.
            to_armature (bpy.types.Object): The target armature object to copy the pose to.
            only_rotation (bool, optional): If True, only copy the rotations. If False, also copy translations and scalings. Defaults to True.
        """
        _LOG.enter()
        rotations = dict()
        translations = dict()
        scalings = dict()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(from_armature)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        for bone in from_armature.pose.bones:
            rotations[bone.name] = bone.rotation_euler.copy()
            translations[bone.name] = bone.location.copy()
            scalings[bone.name] = bone.scale.copy()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(to_armature)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        for bone in to_armature.pose.bones:
            if bone.name in rotations:
                bone.rotation_euler = rotations[bone.name]
            if not only_rotation:
                if bone.name in translations:
                    bone.location = translations[bone.name]
                if bone.name in scalings:
                    bone.scale = scalings[bone.name]

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
