# Part of the legacy "convert to rigify" workflow. This workflow is discouraged
# in new projects; it remains supported only because it is the only viable
# rigify path for characters imported from MakeHuman. For new characters, use
# the modern workflow on the Rigging panel (Add rigify metarig + Generate).

"""This module provides functionality for converting a rig to rigify.

The code is based on an approach suggested by Andrea Rossato in https://www.youtube.com/watch?v=zmsuLD7hAUA
"""

import bpy, json, typing

from ....services import LogService
from ....services import ObjectService
from ....services import SystemService
from ....types import RigifyBoneInfo, RigifySettings, RigifyUi

_LOG = LogService.get_logger("rigifyhelpers.rigifyhelpers")

from ....services import RigService

# The rigify add-on registers both operators and RNA properties of its own, none of which exist in
# the bpy stubs. Operator calls therefore carry a narrow ignore and property accesses go through a
# cast to Any, the same way entities/rig.py reads rigify_type and rigify_parameters off a pose bone.
# Each site is guarded at runtime by SystemService.check_for_rigify().
#
# The RigService bone finders return an optional because the blender collections they read do. Every
# lookup below names a bone from one of the get_list_of_*_bones() lists, which the concrete subclass
# defines for the rig it was selected for, so the casts record a contract the caller is expected to
# satisfy rather than a guarantee pyright can check.

class RigifyHelpers():

    """This is the abstract rig type independent base class for working with
    rigify. You will want to call the static get_instance() method to get a
    concrete implementation for the specific rig you are working with."""

    def __init__(self, settings: RigifySettings) -> None:
        """Get a new instance of RigifyHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing RigifyHelpers object")
        self.settings = settings
        _LOG.dump("settings", self.settings)
        self.produce = "produce" in settings and settings["produce"]
        self.meta_rig_action = str(settings.get("meta_rig_action", "hide") or "hide").lower()

    @staticmethod
    def get_instance(settings: RigifySettings, rigtype: str="Default") -> "RigifyHelpers":
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        from .gameenginerigifyhelpers import GameEngineRigifyHelpers  # pylint: disable=C0415
        return GameEngineRigifyHelpers(settings)

    def convert_to_rigify(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()

        # This should never happen as we check for rigify in the operators, but it is here as a fallback.
        if not SystemService.check_for_rigify():
            _LOG.error("Rigify is not installed/enabled")
            raise NotImplementedError('Rigify is not enabled. Enable it to use this feature.')

        from ...objectproperties import GeneralObjectProperties
        scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=armature_object)

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
            armature_data = typing.cast(bpy.types.Armature, armature_object.data)
            if hasattr(armature_data, 'rigify_rig_basename'):
                typing.cast(typing.Any, armature_data).rigify_rig_basename = target_name
            else:
                armature_object.name = target_name

        if self.produce:

            bpy.ops.armature.rigify_collection_set_ui_row(index=0, row=1)  # pyright: ignore[reportAttributeAccessIssue]
            bpy.ops.pose.rigify_generate()  # pyright: ignore[reportAttributeAccessIssue]

            # rigify_generate() leaves the rig it produced as the active object.
            rigify_object = typing.cast(bpy.types.Object, bpy.context.active_object)
            rigify_object.show_in_front = True

            self.adjust_children_for_rigify(rigify_object, armature_object)

            if self.meta_rig_action == "delete":
                bpy.data.objects.remove(armature_object, do_unlink=True)
            elif self.meta_rig_action == "hide":
                armature_object.hide_viewport = True
                armature_object.hide_render = True

            GeneralObjectProperties.set_value("scale_factor", scale_factor, entity_reference=rigify_object)
            GeneralObjectProperties.set_value("object_type", "Skeleton", entity_reference=rigify_object)

    @staticmethod
    def adjust_children_for_rigify(rigify_object: bpy.types.Object, armature_object: bpy.types.Object) -> None:
        # Build lists first, because adjusting changes parents
        child_rigs = list(ObjectService.find_related_skeletons(armature_object, only_children=True))
        child_meshes = list(ObjectService.find_related_mesh_base_or_assets(armature_object, only_children=True))

        for child_rig in child_rigs:
            RigifyHelpers.adjust_skeleton_for_rigify(child_rig, rigify_object, armature_object)

        for child_mesh in child_meshes:
            RigifyHelpers.adjust_mesh_for_rigify(child_mesh, rigify_object, armature_object)

    @staticmethod
    def adjust_skeleton_for_rigify(child_rig: bpy.types.Object, rigify_object: bpy.types.Object,
                                   old_armature: bpy.types.Object) -> None:
        if child_rig == rigify_object or child_rig == old_armature:
            return

        from ...rig import Rig

        for bone in typing.cast(bpy.types.Pose, child_rig.pose).bones:
            for con in bone.constraints:
                if con.type == "ARMATURE":
                    armature_con = typing.cast(bpy.types.ArmatureConstraint, con)

                    # As a special case, convert armature constraints bound to a vertex to deform bones
                    if ObjectService.object_is_subrig(child_rig) and \
                            Rig.get_armature_constraint_vertex_index(armature_con) is not None:
                        convert = RigifyHelpers._to_def_bone
                    else:
                        convert = RigifyHelpers._to_org_bone

                    for tgt in armature_con.targets:
                        if tgt.target == old_armature:
                            tgt.target = rigify_object
                            tgt.subtarget = convert(tgt.subtarget, rigify_object)
                else:
                    # target and subtarget are declared on the concrete constraint subclasses rather
                    # than on Constraint, and which ones carry them is exactly what the getattr and
                    # hasattr tests below establish.
                    con_any = typing.cast(typing.Any, con)

                    if getattr(con, "target", None) == old_armature:
                        con_any.target = rigify_object

                        if hasattr(con, "subtarget"):
                            con_any.subtarget = RigifyHelpers._to_org_bone(con_any.subtarget, rigify_object)

        if child_rig.parent == old_armature:
            child_rig.parent = rigify_object

    @staticmethod
    def adjust_mesh_for_rigify(child_mesh: bpy.types.Object, rigify_object: bpy.types.Object,
                               old_armature: bpy.types.Object) -> None:
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
    def _to_org_bone(name: str, rigify_object: bpy.types.Object) -> str:
        org_name = "ORG-" + name

        if org_name in typing.cast(bpy.types.Pose, rigify_object.pose).bones:
            return org_name
        else:
            return name

    @staticmethod
    def _to_def_bone(name: str, rigify_object: bpy.types.Object) -> str:
        org_name = "ORG-" + name
        def_name = "DEF-" + name

        pose_bones = typing.cast(bpy.types.Pose, rigify_object.pose).bones

        if org_name in pose_bones and def_name in pose_bones:
            return def_name
        else:
            return name

    @staticmethod
    def load_rigify_ui(armature_object: bpy.types.Object, rigify_ui: RigifyUi | None) -> None:
        assert armature_object == bpy.context.active_object

        # This should never happen as we check for rigify in the operators, but it is here as a fallback.
        if not SystemService.check_for_rigify():
            _LOG.error("Rigify is not installed/enabled")
            raise NotImplementedError('Rigify is not enabled. Enable it to use this feature.')

        if not rigify_ui:
            return

        bpy.ops.armature.rigify_add_color_sets()  # pyright: ignore[reportAttributeAccessIssue]

        armature_data = typing.cast(bpy.types.Armature, armature_object.data)
        rigify_data = typing.cast(typing.Any, armature_data)

        rigify_data.rigify_colors_lock = rigify_ui["rigify_colors_lock"]
        rigify_data.rigify_selection_colors.select = rigify_ui["selection_colors"]["select"]
        rigify_data.rigify_selection_colors.active = rigify_ui["selection_colors"]["active"]

        for _ in range(len(rigify_ui["colors"]) - len(rigify_data.rigify_colors)):
            rigify_data.rigify_colors.add()

        for color, col in zip(rigify_data.rigify_colors, rigify_ui["colors"]):
            color.name = col["name"]
            color.normal = col["normal"]

        collections = armature_data.collections

        for bcoll_name, bcoll_info in rigify_ui["collections"].items():
            bcoll = collections[bcoll_name]
            bcoll.is_visible = bcoll_info["is_visible"]
            rigify_bcoll = typing.cast(typing.Any, bcoll)
            rigify_bcoll.rigify_ui_row = bcoll_info["ui_row"]
            rigify_bcoll.rigify_ui_title = bcoll_info["ui_title"]
            rigify_bcoll.rigify_sel_set = bcoll_info["sel_set"]
            rigify_bcoll.rigify_color_set_id = bcoll_info["color_set_id"]

    @staticmethod
    def get_rigify_ui(armature_object: bpy.types.Object) -> RigifyUi | None:
        if not SystemService.check_for_rigify():
            return None

        armature_data = typing.cast(bpy.types.Armature, armature_object.data)
        rigify_data = typing.cast(typing.Any, armature_data)

        if (len(rigify_data.rigify_colors) == 0 and
                not any(typing.cast(typing.Any, bcoll).rigify_ui_row > 0 for bcoll in armature_data.collections)):
            return None

        rigify_ui: RigifyUi = dict()
        rigify_ui["selection_colors"] = dict()

        rigify_ui["rigify_colors_lock"] = rigify_data.rigify_colors_lock
        rigify_ui["selection_colors"]["select"] = list(rigify_data.rigify_selection_colors.select)
        rigify_ui["selection_colors"]["active"] = list(rigify_data.rigify_selection_colors.active)

        rigify_ui["colors"] = []

        for color in rigify_data.rigify_colors:
            col = dict()
            col["name"] = str(color.name)
            col["normal"] = color["normal"].to_list()
            rigify_ui["colors"].append(col)

        rigify_ui["collections"] = {}

        for bcoll in armature_data.collections:
            rigify_bcoll = typing.cast(typing.Any, bcoll)
            rigify_ui["collections"][bcoll.name] = {
                "is_visible": bcoll.is_visible,
                "ui_row": rigify_bcoll.rigify_ui_row,
                "ui_title": rigify_bcoll.rigify_ui_title,
                "sel_set": rigify_bcoll.rigify_sel_set,
                "color_set_id": rigify_bcoll.rigify_color_set_id,
            }

        return rigify_ui

    @staticmethod
    def upgrade_rigify_layer_refs(rigify: RigifyBoneInfo, coll_names: list[str], coll_used: set[int]) -> None:
        default_layers = [i == 1 for i in range(32)]
        default_map = {
            'faces.super_face': ['primary', 'secondary'],
            'limbs.arm': ['fk', 'tweak'],
            'limbs.front_paw': ['fk', 'tweak'],
            'limbs.leg': ['fk', 'tweak'],
            'limbs.paw': ['fk', 'tweak'],
            'limbs.rear_paw': ['fk', 'tweak'],
            'limbs.simple_tentacle': ['tweak'],
            'limbs.super_finger': ['tweak'],
            'limbs.super_limb': ['fk', 'tweak'],
            'spines.basic_spine': ['fk', 'tweak'],
        }

        if params := rigify.get("rigify_parameters"):
            # A bone with no rigify_type is the normal case, and dict.get() takes any hashable at
            # runtime, while typeshed narrows the key to the dict's own key type.
            if default_list := default_map.get(rigify.get("rigify_type")):  # pyright: ignore[reportArgumentType]
                for name in default_list:
                    if params.get(name + "_layers_extra", True) and (name + "_layers") not in params:
                        params[name + "_layers"] = default_layers

            for param_name, param_value in list(params.items()):
                if (param_name.endswith("_layers") and isinstance(param_value, list)
                        and len(param_value) == 32):
                    used = set(i for i, v in enumerate(param_value) if v)
                    params[param_name[:-7] + "_coll_refs"] = [coll_names[i] for i in sorted(used)]
                    coll_used |= used
                    del params[param_name]

    @staticmethod
    def upgrade_rigify_ui_layers(rigify_ui: RigifyUi, coll_names: list[str], coll_used: set[int]) -> None:

        if SystemService.check_for_rigify():
            # This workaround is only here in the hope that VSCode will stop complaining about the import.
            # The code always worked, but VSCode does not seem to recognize the module, even though
            # the "rigify.utils.rig" module is available under scripts/addons_core/rigify after having
            # installed an official version of Blender
            import rigify  # type: ignore
            from rigify.utils.rig import resolve_layer_names  # type: ignore

        resolved_names = resolve_layer_names(rigify_ui["rigify_layers"])

        for i, name in enumerate(resolved_names):
            if name:
                coll_names[i] = name

        coll_names[28] = "Root"
        coll_names[29] = "DEF"
        coll_names[30] = "MCH"
        coll_names[31] = "ORG"

        collections = {}

        for i, info in enumerate(rigify_ui["rigify_layers"]):
            name = info["name"].strip()
            if name and i <= 28:
                coll_used.add(i)
                collections[coll_names[i]] = {
                    "is_visible": True,  # Unlike 3.6, in 4.0 this affects visibility of generated layers
                    "ui_row": info["row"],
                    "ui_title": "" if name == coll_names[i] else name,
                    "sel_set": info["selset"],
                    "color_set_id": info["group"],
                }

        if "Root" in collections:
            collections["Root"]["ui_row"] = 3 + max(v["ui_row"] for k, v in collections.items() if k != "Root")

        rigify_ui["collections"] = collections

        del rigify_ui["layers"]
        del rigify_ui["rigify_layers"]

    def _set_use_connect_on_bones(self, armature_object: bpy.types.Object, bone_names: list[str],
                                  exclude_first: bool=True) -> None:
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        if exclude_first:
            bone_names = list(bone_names)  # to modify a copy rather than the source list
            bone_names.pop(0)

        for bone_name in bone_names:
            _LOG.debug("About to set use_connect on", bone_name)
            edit_bone = typing.cast(bpy.types.EditBone, RigService.find_edit_bone_by_name(bone_name, armature_object))
            edit_bone.use_connect = True
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _setup_spine(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        spine = self.get_list_of_spine_bones()  # pylint: disable=E1111
        _LOG.dump("Spine", spine)
        self._set_use_connect_on_bones(armature_object, spine)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        first_spine_bone = typing.cast(typing.Any, RigService.find_pose_bone_by_name(spine[0], armature_object))
        first_spine_bone.rigify_type = 'spines.basic_spine'
        first_spine_bone.rigify_parameters.segments = len(spine)
        # TODO: change layers

    def _setup_arms(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for side in [True, False]:
            arm = self.get_list_of_arm_bones(side)  # pylint: disable=E1111
            _LOG.dump("Arm", arm)
            self._set_use_connect_on_bones(armature_object, arm)
            first_arm_bone = typing.cast(typing.Any, RigService.find_pose_bone_by_name(arm[0], armature_object))
            first_arm_bone.rigify_type = 'limbs.arm'
            # first_arm_bone.rigify_parameters.segments = len(arm)
        # TODO: change layers

    def _setup_legs(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        for side in [True, False]:
            leg = self.get_list_of_leg_bones(side)  # pylint: disable=E1111
            _LOG.dump("Leg", leg)
            self._set_use_connect_on_bones(armature_object, leg)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            toe_bone_name = leg[-1]
            toe = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(toe_bone_name, armature_object))
            toe_bone_head = toe.head
            toe_bone_length = toe.length
            _LOG.debug("Toe bone", (toe_bone_name, toe_bone_head, toe_bone_length))

            foot_bone_name = self.get_foot_name(side)
            _LOG.debug("Foot bone name", foot_bone_name)
            foot = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(foot_bone_name, armature_object))
            foot_bone_head = foot.head
            foot_bone_length = foot.length
            _LOG.debug("Foot bone data", (foot_bone_head, foot_bone_length))

            first_leg_bone = typing.cast(typing.Any, RigService.find_pose_bone_by_name(leg[0], armature_object))
            first_leg_bone.rigify_type = 'limbs.leg'

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            bone_side = 'R'
            if side:
                bone_side = 'L'

            bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
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

    def _setup_shoulders(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        for side in [True, False]:
            shoulder = self.get_list_of_shoulder_bones(side)  # pylint: disable=E1111
            _LOG.dump("Shoulder", shoulder)
            self._set_use_connect_on_bones(armature_object, shoulder)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            first_shoulder_bone = typing.cast(typing.Any, RigService.find_pose_bone_by_name(shoulder[0], armature_object))
            first_shoulder_bone.rigify_type = 'basic.super_copy'

    def _setup_head(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        head = self.get_list_of_head_bones()  # pylint: disable=E1111
        _LOG.dump("Head", head)
        self._set_use_connect_on_bones(armature_object, head)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        first_head_bone = typing.cast(typing.Any, RigService.find_pose_bone_by_name(head[0], armature_object))
        first_head_bone.rigify_type = 'spines.super_head'

    def _setup_fingers(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        for side in [True, False]:
            for finger_number in range(5):
                finger = self.get_list_of_finger_bones(finger_number, side)  # pylint: disable=E1111
                _LOG.dump("Finger", finger)
                self._set_use_connect_on_bones(armature_object, finger)
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                first_finger_bone = typing.cast(typing.Any, RigService.find_pose_bone_by_name(finger[0], armature_object))
                first_finger_bone.rigify_type = 'limbs.super_finger'

    def get_foot_name(self, left_side: bool=True) -> str:
        """Abstract method for getting the name of a foot bone, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_foot_name() method must be overriden by the rig class")

    def get_list_of_spine_bones(self) -> list[str]:
        """Abstract method for getting a list of bones in the spine, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_spine_bones() method must be overriden by the rig class")

    def get_list_of_arm_bones(self, left_side: bool=True) -> list[str]:
        """Abstract method for getting a list of bones in an arm, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_arm_bones() method must be overriden by the rig class")

    def get_list_of_leg_bones(self, left_side: bool=True) -> list[str]:
        """Abstract method for getting a list of bones in a leg, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_leg_bones() method must be overriden by the rig class")

    def get_list_of_shoulder_bones(self, left_side: bool=True) -> list[str]:
        """Abstract method for getting a list of bones in a shoulder, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_shoulder_bones() method must be overriden by the rig class")

    def get_list_of_head_bones(self) -> list[str]:
        """Abstract method for getting a list of bones in the head, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_head_bones() method must be overriden by the rig class")

    def get_list_of_finger_bones(self, finger_number: int, left_side: bool=True) -> list[str]:
        """Abstract method for getting a list of bones in a finger, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_finger_bones() method must be overriden by the rig class")
