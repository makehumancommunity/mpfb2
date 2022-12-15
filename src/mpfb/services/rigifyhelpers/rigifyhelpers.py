"""This module provides functionality for converting a rig to rigify.

The code is based on an approach suggested by Andrea Rossato in https://www.youtube.com/watch?v=zmsuLD7hAUA
"""

import bpy, json

from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.systemservice import SystemService

_LOG = LogService.get_logger("rigifyhelpers.rigifyhelpers")

from mpfb.services.rigservice import RigService

class RigifyHelpers():

    """This is the abstract rig type independent base class for working with
    rigify. You will want to call the static get_instance() method to get a
    concrete implementation for the specific rig you are working with."""

    def __init__(self, settings):
        """Get a new instance of RigifyHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing RigifyHelpers object")
        self.settings = settings
        _LOG.dump("settings", self.settings)
        self.produce = "produce" in settings and settings["produce"]
        self.keep_meta = "keep_meta" in settings and settings["keep_meta"]

    @staticmethod
    def get_instance(settings, rigtype="Default"):
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        from mpfb.services.rigifyhelpers.gameenginerigifyhelpers import GameEngineRigifyHelpers  # pylint: disable=C0415
        return GameEngineRigifyHelpers(settings)

    def convert_to_rigify(self, armature_object):
        _LOG.enter()

        self._setup_spine(armature_object)
        self._setup_arms(armature_object)
        self._setup_legs(armature_object)
        self._setup_shoulders(armature_object)
        self._setup_head(armature_object)
        self._setup_fingers(armature_object)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        name = armature_object.name

        if "name" in self.settings:
            name = str(self.settings["name"]).strip()

        if name:
            target_name = name
            if ObjectService.object_name_exists("RIG-" + name):
                target_name = ObjectService.ensure_unique_name("RIG-" + name)
                target_name = target_name.replace("RIG-", "")
            if hasattr(armature_object.data, 'rigify_rig_basename'):
                armature_object.data.rigify_rig_basename = target_name
            else:
                armature_object.name = target_name

        if self.produce:
            bpy.ops.pose.rigify_generate()

            rigify_object = bpy.context.active_object
            rigify_object.show_in_front = True

            self.adjust_children_for_rigify(rigify_object, armature_object)

            if not self.keep_meta:
                bpy.data.objects.remove(armature_object, do_unlink=True)

    @staticmethod
    def adjust_children_for_rigify(rigify_object, armature_object):
        # Build lists first, because adjusting changes parents
        child_rigs = list(ObjectService.find_related_skeletons(armature_object, only_children=True))
        child_meshes = list(ObjectService.find_related_mesh_base_or_assets(armature_object, only_children=True))

        for child_rig in child_rigs:
            RigifyHelpers.adjust_skeleton_for_rigify(child_rig, rigify_object, armature_object)

        for child_mesh in child_meshes:
            RigifyHelpers.adjust_mesh_for_rigify(child_mesh, rigify_object, armature_object)

    @staticmethod
    def adjust_skeleton_for_rigify(child_rig, rigify_object, old_armature):
        if child_rig == rigify_object or child_rig == old_armature:
            return

        from mpfb.entities.rig import Rig

        for bone in child_rig.pose.bones:
            for con in bone.constraints:
                if con.type == "ARMATURE":
                    # As a special case, convert armature constraints bound to a vertex to deform bones
                    if ObjectService.object_is_subrig(child_rig) and \
                            Rig.get_armature_constraint_vertex_index(con) is not None:
                        convert = RigifyHelpers._to_def_bone
                    else:
                        convert = RigifyHelpers._to_org_bone

                    for tgt in con.targets:
                        if tgt.target == old_armature:
                            tgt.target = rigify_object
                            tgt.subtarget = convert(tgt.subtarget, rigify_object)
                else:
                    if getattr(con, "target", None) == old_armature:
                        con.target = rigify_object

                        if hasattr(con, "subtarget"):
                            con.subtarget = RigifyHelpers._to_org_bone(con.subtarget, rigify_object)

        if child_rig.parent == old_armature:
            child_rig.parent = rigify_object

    @staticmethod
    def adjust_mesh_for_rigify(child_mesh, rigify_object, old_armature):
        for vertex_group in child_mesh.vertex_groups:
            def_name = RigifyHelpers._to_def_bone(vertex_group.name, rigify_object)

            if def_name != vertex_group.name:
                _LOG.debug("Renaming vertex group", (child_mesh.name, vertex_group.name, def_name))
                vertex_group.name = def_name

        for modifier in child_mesh.modifiers:
            if isinstance(modifier, bpy.types.ArmatureModifier) and modifier.object == old_armature:
                modifier.object = rigify_object

        if child_mesh.parent == old_armature:
            child_mesh.parent = rigify_object

    @staticmethod
    def _to_org_bone(name, rigify_object):
        org_name = "ORG-" + name

        if org_name in rigify_object.pose.bones:
            return org_name
        else:
            return name

    @staticmethod
    def _to_def_bone(name, rigify_object):
        org_name = "ORG-" + name
        def_name = "DEF-" + name

        if org_name in rigify_object.pose.bones and def_name in rigify_object.pose.bones:
            return def_name
        else:
            return name

    @staticmethod
    def load_rigify_ui(armature_object, rigify_ui):
        assert armature_object == bpy.context.active_object

        if not rigify_ui or not SystemService.check_for_rigify():
            return

        bpy.ops.armature.rigify_add_bone_groups()
        bpy.ops.pose.rigify_layer_init()

        armature_object.data.rigify_colors_lock = rigify_ui["rigify_colors_lock"]
        armature_object.data.rigify_selection_colors.select = rigify_ui["selection_colors"]["select"]
        armature_object.data.rigify_selection_colors.active = rigify_ui["selection_colors"]["active"]

        for _ in range(len(rigify_ui["colors"]) - len(armature_object.data.rigify_colors)):
            armature_object.data.rigify_colors.add()

        for color, col in zip(armature_object.data.rigify_colors, rigify_ui["colors"]):
            color.name = col["name"]
            color.normal = col["normal"]

        armature_object.data.layers = rigify_ui["layers"]

        for rigify_layer, layer in zip(armature_object.data.rigify_layers, rigify_ui["rigify_layers"]):
            rigify_layer.name = layer["name"]
            rigify_layer.row = layer["row"]
            rigify_layer.selset = layer["selset"]
            rigify_layer.group = layer["group"]

    @staticmethod
    def get_rigify_ui(armature_object):
        if not SystemService.check_for_rigify():
            return None

        if len(armature_object.data.rigify_layers) == 0:
            return None

        rigify_ui = dict()
        rigify_ui["selection_colors"] = dict()

        rigify_ui["rigify_colors_lock"] = armature_object.data.rigify_colors_lock
        rigify_ui["selection_colors"]["select"] = list(armature_object.data.rigify_selection_colors.select)
        rigify_ui["selection_colors"]["active"] = list(armature_object.data.rigify_selection_colors.active)

        rigify_ui["colors"] = []

        for color in armature_object.data.rigify_colors:
            col = dict()
            col["name"] = str(color.name)
            col["normal"] = color["normal"].to_list()
            rigify_ui["colors"].append(col)

        rigify_ui["layers"] = []
        for layer in armature_object.data.layers:
            rigify_ui["layers"].append(layer)

        rigify_ui["rigify_layers"] = []

        for rigify_layer in armature_object.data.rigify_layers:
            layer = dict()
            layer["name"] = rigify_layer.name
            layer["row"] = rigify_layer.row
            layer["selset"] = rigify_layer.selset
            layer["group"] = rigify_layer.group

            rigify_ui["rigify_layers"].append(layer)

        return rigify_ui

    def _set_use_connect_on_bones(self, armature_object, bone_names, exclude_first=True):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        if exclude_first:
            bone_names = list(bone_names) # to modify a copy rather than the source list
            bone_names.pop(0)

        for bone_name in bone_names:
            _LOG.debug("About to set use_connect on", bone_name)
            edit_bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
            edit_bone.use_connect = True
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _setup_spine(self, armature_object):
        _LOG.enter()
        spine = self.get_list_of_spine_bones() # pylint: disable=E1111
        _LOG.dump("Spine", spine)
        self._set_use_connect_on_bones(armature_object, spine)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        first_spine_bone = RigService.find_pose_bone_by_name(spine[0], armature_object)
        first_spine_bone.rigify_type = 'spines.basic_spine'
        first_spine_bone.rigify_parameters.segments = len(spine)
        # TODO: change layers

    def _setup_arms(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for side in [True, False]:
            arm = self.get_list_of_arm_bones(side) # pylint: disable=E1111
            _LOG.dump("Arm", arm)
            self._set_use_connect_on_bones(armature_object, arm)
            first_arm_bone = RigService.find_pose_bone_by_name(arm[0], armature_object)
            first_arm_bone.rigify_type = 'limbs.arm'
            #first_arm_bone.rigify_parameters.segments = len(arm)
        # TODO: change layers

    def _setup_legs(self, armature_object):
        _LOG.enter()
        for side in [True, False]:
            leg = self.get_list_of_leg_bones(side) # pylint: disable=E1111
            _LOG.dump("Leg", leg)
            self._set_use_connect_on_bones(armature_object, leg)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            toe_bone_name = leg[-1]
            toe = RigService.find_pose_bone_by_name(toe_bone_name, armature_object)
            toe_bone_head = toe.head
            toe_bone_length = toe.length
            _LOG.debug("Toe bone", (toe_bone_name, toe_bone_head, toe_bone_length))

            foot_bone_name = self.get_foot_name(side)
            _LOG.debug("Foot bone name", foot_bone_name)
            foot = RigService.find_pose_bone_by_name(foot_bone_name, armature_object)
            foot_bone_head = foot.head
            foot_bone_length = foot.length
            _LOG.debug("Foot bone data", (foot_bone_head, foot_bone_length))

            first_leg_bone = RigService.find_pose_bone_by_name(leg[0], armature_object)
            first_leg_bone.rigify_type = 'limbs.leg'

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            bone_side = 'R'
            if side:
                bone_side = 'L'

            bones = armature_object.data.edit_bones
            bone = bones.new("heel.02." + bone_side)

            head = [toe_bone_head[0], foot_bone_head[1], toe_bone_head[2]]
            tail = [toe_bone_head[0], foot_bone_head[1], toe_bone_head[2]]
            if side:
                head[0] = head[0] - toe_bone_length / 2
                tail[0] = tail[0] + toe_bone_length / 2
            else:
                head[0] = head[0] + toe_bone_length / 2
                tail[0] = tail[0] - toe_bone_length / 2

            bone.head = head
            bone.tail = tail

            foot = RigService.find_edit_bone_by_name(foot_bone_name, armature_object)
            bone.parent = foot

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)


    def _setup_shoulders(self, armature_object):
        _LOG.enter()
        for side in [True, False]:
            shoulder = self.get_list_of_shoulder_bones(side) # pylint: disable=E1111
            _LOG.dump("Shoulder", shoulder)
            self._set_use_connect_on_bones(armature_object, shoulder)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            first_shoulder_bone = RigService.find_pose_bone_by_name(shoulder[0], armature_object)
            first_shoulder_bone.rigify_type = 'basic.super_copy'

    def _setup_head(self, armature_object):
        _LOG.enter()
        head = self.get_list_of_head_bones() # pylint: disable=E1111
        _LOG.dump("Head", head)
        self._set_use_connect_on_bones(armature_object, head)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        first_head_bone = RigService.find_pose_bone_by_name(head[0], armature_object)
        first_head_bone.rigify_type = 'spines.super_head'

    def _setup_fingers(self, armature_object):
        _LOG.enter()
        for side in [True, False]:
            for finger_number in range(5):
                finger = self.get_list_of_finger_bones(finger_number, side) # pylint: disable=E1111
                _LOG.dump("Finger", finger)
                self._set_use_connect_on_bones(armature_object, finger)
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                first_finger_bone = RigService.find_pose_bone_by_name(finger[0], armature_object)
                first_finger_bone.rigify_type = 'limbs.super_finger'

    def get_foot_name(self, left_side=True):
        """Abstract method for getting the name of a foot bone, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_foot_name() method must be overriden by the rig class")

    def get_list_of_spine_bones(self):
        """Abstract method for getting a list of bones in the spine, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_spine_bones() method must be overriden by the rig class")

    def get_list_of_arm_bones(self, left_side=True):
        """Abstract method for getting a list of bones in an arm, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_arm_bones() method must be overriden by the rig class")

    def get_list_of_leg_bones(self, left_side=True):
        """Abstract method for getting a list of bones in a leg, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_leg_bones() method must be overriden by the rig class")

    def get_list_of_shoulder_bones(self, left_side=True):
        """Abstract method for getting a list of bones in a shoulder, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_shoulder_bones() method must be overriden by the rig class")

    def get_list_of_head_bones(self):
        """Abstract method for getting a list of bones in the head, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_head_bones() method must be overriden by the rig class")

    def get_list_of_finger_bones(self, finger_number, left_side=True):
        """Abstract method for getting a list of bones in a finger, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_finger_bones() method must be overriden by the rig class")
