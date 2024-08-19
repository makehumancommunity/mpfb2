"""This module contains functionality for serializing/deserializing rigs via JSON."""

import bmesh

from ..services import LogService
from ..services import ObjectService
from ..services import RigService
from .objectproperties import GeneralObjectProperties

import bpy, math, json, random, typing, re

from bl_math import lerp
from itertools import accumulate
from mathutils import Vector, Matrix, Euler, Quaternion
from mathutils.kdtree import KDTree

_LOG = LogService.get_logger("entities.rig")

_MAX_ALLOWED_DIST = 0.01
_MAX_DIST_TO_CONSIDER_EXACT = 0.001
_STRATEGY_REPLACE_THRESHOLD = 0.0001
_MEAN_LENGTH_PENALTY = 1.0  # Higher penalizes distant vertex pairs more

CLOSE_MEAN_SEARCH_RADIUS = _MAX_ALLOWED_DIST * 2

CUR_VERSION = 110


class Rig:

    """Entity class representing an armature."""

    armature_object: bpy.types.Object

    def __init__(self, basemesh, armature=None, *, parent: typing.Optional['Rig']=None):
        """You might want to use one of the static methods rather than calling init directly."""
        self.basemesh = basemesh
        self.armature_object = armature
        self.parent = parent
        self.position_info = dict()
        self.rig_definition = dict()
        self.rig_header = {
            "bones": self.rig_definition,
            "is_subrig": bool(parent),
            "version": CUR_VERSION,
        }
        self.lowest_point = 1000.0
        self.bad_constraint_targets = set()
        self.relative_scale = 1.0

    @staticmethod
    def from_json_file_and_basemesh(filename, basemesh, *, parent=None):
        """Create an instance of Rig and populate it with information from the json file and from the base mesh."""
        rig = Rig(basemesh, parent=parent)

        with open(filename, "r") as json_file:
            json_data = json.load(json_file)

            if "bones" in json_data:
                if "version" not in json_data:
                    raise ValueError("Invalid rig file format")

                if "joints" in json_data:
                    raise ValueError("MPFB is not compatible with mhskel files")

                if json_data.get("is_subrig", False) and not parent:
                    raise ValueError("Attempting to load a sub-rig without a parent")

                rig.rig_header = json_data
                rig.rig_definition = json_data["bones"]

            else:
                rig.rig_header["version"] = 100
                rig.rig_definition.update(json_data)

        if rig._upgrade_definition():
            _LOG.debug("Upgraded the rig definition version")

            # with open(filename + ".new", "w") as json_file:
            #     json.dump(rig.rig_header, json_file, indent=4, sort_keys=True)

        if rig.rig_header.get("scale_factor"):
            scale_factor = GeneralObjectProperties.get_value(
                "scale_factor", entity_reference=parent.basemesh if parent else basemesh)
            if scale_factor:
                rig.relative_scale = scale_factor / rig.rig_header["scale_factor"]

        rig.build_basemesh_position_info()
        return rig

    def _upgrade_definition(self):
        version = self.rig_header["version"]
        if version == CUR_VERSION:
            return False

        if version > CUR_VERSION:
            raise ValueError(f"The rig file format version is too high: {version}")

        # Upgrade from layers to collections
        if version < 110:
            from .rigging.rigifyhelpers.rigifyhelpers import RigifyHelpers

            coll_names = [f"Layer {i+1}" for i in range(32)]
            coll_used = set()

            # Upgrade Rigify UI data
            if rigify_ui := self.rig_header.get("rigify_ui"):
                RigifyHelpers.upgrade_rigify_ui_layers(rigify_ui, coll_names, coll_used)
            else:
                coll_names[0] = "Bones"

            # Upgrade bone data
            for bone_info in self.rig_definition.values():
                # Layers the bone is assigned to
                if layers := bone_info.get("layers"):
                    used = set(i for i, v in enumerate(layers) if v)
                    bone_info["collections"] = sorted(coll_names[i] for i in used)
                    coll_used |= used
                    del bone_info["layers"]

                # Layer references in rigify parameters
                if rigify := bone_info.get("rigify"):
                    RigifyHelpers.upgrade_rigify_layer_refs(rigify, coll_names, coll_used)

            # Build the list of used collections
            if len(coll_used) > 0:
                self.rig_header["collections"] = [coll_names[i] for i in sorted(coll_used)]

        self.rig_header["version"] = CUR_VERSION
        return True

    @staticmethod
    def from_given_armature_context(armature_object: bpy.types.Object | None, *,
                                    is_subrig: bool | None=None, operator=None,
                                    empty=False, fast_positions=False, rigify_ui=False):
        """Create an instance of Rig and populate it with information from the armature and related meshes."""

        base_rig, basemesh, direct_mesh = ObjectService.find_armature_context_objects(
            armature_object, operator=operator, is_subrig=is_subrig)

        if not direct_mesh:
            return None

        if direct_mesh != basemesh:
            parent_rig = Rig.from_given_basemesh_and_armature(basemesh, base_rig, fast_positions=True)

            return Rig.from_given_basemesh_and_armature(
                direct_mesh, armature_object, parent=parent_rig,
                empty=empty, fast_positions=fast_positions, rigify_ui=rigify_ui
            )
        else:
            return Rig.from_given_basemesh_and_armature(
                basemesh, base_rig,
                empty=empty, fast_positions=fast_positions, rigify_ui=rigify_ui
            )

    @staticmethod
    def from_given_basemesh_and_armature(basemesh, armature, *, parent=None, empty=False, fast_positions=False,
                                         rigify_ui=False):
        """Create an instance of Rig and populate it with information from the base mesh
        and from the armature which is expected to be the currently active object."""

        rig = Rig(basemesh, armature, parent=parent)

        if scale_factor := GeneralObjectProperties.get_value(
                "scale_factor", entity_reference=parent.basemesh if parent else basemesh):
            rig.rig_header["scale_factor"] = scale_factor

        rig.build_basemesh_position_info()

        if empty:
            return rig

        rig.rig_header["collections"] = [bcoll.name for bcoll in armature.data.collections]

        rig.add_data_bone_info()

        if fast_positions:
            rig.match_bone_positions_with_strategies(fast=True)

        else:
            assert bpy.context.active_object == armature

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            rig.add_edit_bone_info()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            rig.add_pose_bone_info()

            rig.match_bone_positions_with_strategies()
            rig.restore_saved_strategies()

            rig.cleanup_float_values()

        if extra_bones := RigService.find_extra_bones(rig.armature_object):
            rig.rig_header["extra_bones"] = extra_bones

        if rigify_ui:
            from .rigging.rigifyhelpers.rigifyhelpers import RigifyHelpers
            rig.rig_header["rigify_ui"] = RigifyHelpers.get_rigify_ui(armature)

        return rig

    def create_armature_and_fit_to_basemesh(self, for_developer=False, add_modifier=True):
        """Use the information in the object to construct an armature and adjust it to fit the base mesh."""

        if self.parent:
            # Disable pose evaluation for parent so that any child-of constraints bind to rest pose.
            self.parent.armature_object.data.pose_position = "REST"

        bpy.ops.object.armature_add(location=self.basemesh.location)
        self.armature_object = bpy.context.object

        scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=self.basemesh)
        GeneralObjectProperties.set_value("scale_factor", scale_factor, entity_reference=self.armature_object)

        object_type = "Subrig" if self.parent else "Skeleton"

        GeneralObjectProperties.set_value("object_type", object_type, entity_reference=self.armature_object)

        self.armature_object.show_in_front = True
        self.armature_object.data.display_type = 'WIRE'

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        for bone in self.armature_object.data.edit_bones:
            self.armature_object.data.edit_bones.remove(bone)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)  # To commit removal of bones

        self.create_bone_collections()
        self.create_bones()
        self.update_edit_bone_metadata()
        self.rigify_metadata()

        if for_developer:
            self.save_strategies()

        RigService.set_extra_bones(self.armature_object, self.rig_header.get("extra_bones"))

        if self.rig_header.get("rigify_ui"):
            from .rigging.rigifyhelpers.rigifyhelpers import RigifyHelpers
            RigifyHelpers.load_rigify_ui(self.armature_object, self.rig_header["rigify_ui"])

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if self.parent:
            self.parent.armature_object.data.pose_position = "POSE"

        if add_modifier:
            if self.parent:
                RigService.ensure_armature_modifier(
                    self.basemesh, self.parent.armature_object, subrig=self.armature_object)
            else:
                RigService.ensure_armature_modifier(self.basemesh, self.armature_object)

        return self.armature_object

    def get_best_location_from_strategy(self, head_or_tail_info, use_default=True):
        strategy = head_or_tail_info["strategy"]
        location = None
        try:
            if strategy == "CUBE":
                name = head_or_tail_info["cube_name"]
                location = self.position_info["cubes"].get(name, None)
            elif strategy == "VERTEX":
                index = head_or_tail_info["vertex_index"]
                location = self.position_info["vertices"][index]
            elif strategy == "MEAN":
                indices = head_or_tail_info["vertex_indices"]
                if len(indices) > 0:
                    vertices = [self.position_info["vertices"][i] for i in indices]
                    location = [sum(v[i] for v in vertices) / len(vertices) for i in range(3)]
            elif strategy == "XYZ":
                # Special strategy for Rigify heel marker.
                # Uses different vertices for each coordinate channel.
                indices = head_or_tail_info["vertex_indices"]
                if len(indices) >= 3:
                    vertices = [self.position_info["vertices"][i] for i in indices]
                    location = [vertices[i][i] for i in range(3)]
        except IndexError:
            pass
        if location is not None and "offset" in head_or_tail_info:
            location = [a + b * self.relative_scale for a, b in zip(location, head_or_tail_info["offset"])]
        if location is None and use_default:
            location = head_or_tail_info["default_position"]
        return location

    def _align_roll_by_strategy(self, bone, bone_info):
        self.apply_bone_roll_strategy(bone, bone_info.get("roll_strategy", None))

    @staticmethod
    def apply_bone_roll_strategy(bone, roll_strategy):
        matrix = None

        if roll_strategy == "ALIGN_Z_WORLD_Z":
            matrix = matrix_from_axis_pair(bone.y_axis, (0, 0, 1), 'z')
        elif roll_strategy == "ALIGN_X_WORLD_X":
            matrix = matrix_from_axis_pair(bone.y_axis, (1, 0, 0), 'x')

        if matrix:
            bone.roll = bpy.types.Bone.AxisRollFromMatrix(matrix, axis=bone.y_axis)[1]

    def create_bone_collections(self):
        collections = self.armature_object.data.collections

        if bcoll_names := self.rig_header.get("collections"):
            for bcoll in list(collections):
                collections.remove(bcoll)

            for name in bcoll_names:
                collections.new(name)

        collections.active_index = 0

    def create_bones(self):
        """Create the actual bones in the armature object."""
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bones = self.armature_object.data.edit_bones
        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]
            bone = bones.new(bone_name)
            bone.roll = bone_info["roll"]
            bone.head = self.get_best_location_from_strategy(bone_info["head"])
            bone.tail = self.get_best_location_from_strategy(bone_info["tail"])

            self._align_roll_by_strategy(bone, bone_info)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def reposition_edit_bone(self, *, developer=False):
        """Reposition bones to fit the current state of the basemesh."""
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]
            bone = RigService.find_edit_bone_by_name(bone_name, self.armature_object)
            if bone:
                bone.head = self.get_best_location_from_strategy(bone_info["head"])
                bone.tail = self.get_best_location_from_strategy(bone_info["tail"])
                self._align_roll_by_strategy(bone, bone_info)
            else:
                _LOG.warn("Tried to refit bone that did not exist in definition", bone_name)
                _LOG.debug("Bone info is", bone_info)
                _LOG.dump("Rig definition is", self.rig_definition)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # Reset constraints if present
        updated = False

        for pbone in self.armature_object.pose.bones:
            for con in pbone.constraints:
                if con.type == "STRETCH_TO":
                    con.rest_length = 0
                    updated = True
                elif con.type == "CHILD_OF":
                    con.set_inverse_pending = True
                    updated = True
                elif con.type == "ARMATURE":
                    # When refitting in Developer -> Save Rig, update bones and weights in
                    # Armature constraints referencing a vertex
                    if self.parent and developer:
                        if self._rebuild_armature_con_vertex_targets(con):
                            updated = True

        if updated:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    @staticmethod
    def get_armature_constraint_vertex_index(con: bpy.types.ArmatureConstraint) -> int | None:
        if match := re.fullmatch(r'^VERTEX:\s*(\d+)(\D.*|)$', con.name):
            return int(match.group(1))
        else:
            return None

    @staticmethod
    def ensure_armature_constraint_vertex_index(con: bpy.types.ArmatureConstraint, vertex: int):
        if match := re.fullmatch(r'^VERTEX:\s*(\d+)(\D.*|)$', con.name):
            con.name = f"VERTEX:{vertex}{match.group(2)}"
        else:
            con.name = f"VERTEX:{vertex} {con.name}"

    def _rebuild_armature_con_vertex_targets(self, con: bpy.types.ArmatureConstraint):
        vertex = self.get_armature_constraint_vertex_index(con)

        if vertex is not None:
            weights = self.parent._find_vertex_weights(vertex)

            if weights:
                for tgt in list(con.targets):
                    if tgt.target == self.parent.armature_object:
                        con.targets.remove(tgt)

                for name, weight in weights.items():
                    tgt = con.targets.new()
                    tgt.target = self.parent.armature_object
                    tgt.subtarget = name
                    tgt.weight = weight

                return True

        return False

    def update_edit_bone_metadata(self):
        """Assign metadata fitting for the edit bones."""
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]
            bone = RigService.find_edit_bone_by_name(bone_name, self.armature_object)
            if bone_info["parent"]:
                bone.parent = RigService.find_edit_bone_by_name(bone_info["parent"], self.armature_object)
            bone.use_connect = bone_info["use_connect"]
            bone.use_local_location = bone_info["use_local_location"]
            bone.use_inherit_rotation = bone_info["use_inherit_rotation"]
            bone.inherit_scale = bone_info["inherit_scale"]

            if coll_names := bone_info.get("collections"):
                for name in coll_names:
                    self.armature_object.data.collections[name].assign(bone)
            else:
                self.armature_object.data.collections.active.assign(bone)

            if "bendy_bone" in bone_info:
                for field, val in bone_info["bendy_bone"].items():
                    if field in ("custom_handle_start", "custom_handle_end"):
                        val = RigService.find_edit_bone_by_name(val, self.armature_object)

                    setattr(bone, "bbone_" + field, val)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def rigify_metadata(self):
        """Assign bone meta data fitting for the pose bones."""
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for bone_name, bone_info in self.rig_definition.items():
            bone = RigService.find_pose_bone_by_name(bone_name, self.armature_object)

            bone.rotation_mode = bone_info.get("rotation_mode", "QUATERNION")

            for con_info in bone_info.get("constraints", []):
                self._apply_constraint_info(bone, con_info)

            rigify = bone_info["rigify"]

            if "rigify_type" in rigify and rigify["rigify_type"]:
                bone.rigify_type = rigify["rigify_type"]

            if "rigify_parameters" in rigify:
                for key in rigify["rigify_parameters"].keys():
                    value = rigify["rigify_parameters"][key]
                    _LOG.debug("Will attempt to set bone.parameters.", key)
                    if key.endswith("_coll_refs"):
                        ref_list = getattr(bone.rigify_parameters, key, None)
                        if ref_list is not None and hasattr(ref_list, 'add'):
                            for name in value:
                                ref = ref_list.add()
                                ref.name = name
                        else:
                            _LOG.error("Rigify bone collection reference list not found.", key)
                    else:
                        try:
                            setattr(bone.rigify_parameters, str(key), value)
                        except AttributeError:
                            _LOG.error("Rigify bone parameter not found.", key)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _apply_constraint_info(self, bone: bpy.types.PoseBone, info):
        con = bone.constraints.new(info["type"])
        con.name = info["name"]

        if isinstance(con, bpy.types.ArmatureConstraint):
            for tgt_info in info["targets"]:
                tgt = con.targets.new()

                if "target" in tgt_info:
                    tgt.target = self._restore_parent_ref(bone, tgt_info["target"], tgt_info)
                else:
                    tgt.target = self.armature_object

                tgt.subtarget = tgt_info["subtarget"]
                tgt.weight = tgt_info["weight"]

            if parent_ref := info.get("target"):
                assert parent_ref["strategy"] == "VERTEX"

                vertex = parent_ref["vertex_index"]

                # Just in case ensure the name reflects the result
                self.ensure_armature_constraint_vertex_index(con, vertex)

                for name, weight in self.parent._find_vertex_weights(vertex).items():
                    tgt = con.targets.new()
                    tgt.target = self.parent.armature_object
                    tgt.subtarget = name
                    tgt.weight = weight

        else:
            target = info.get("target", False)

            if target is True:
                con.target = self.armature_object
            elif isinstance(target, dict):
                con.target = self._restore_parent_ref(bone, target, info)
            else:
                assert not target

        if info.get("space_object", False):
            con.space_object = self.armature_object

        skip_list = {"type", "name", "targets", "target", "space_object"}

        for field, val in info.items():
            if field not in skip_list:
                setattr(con, field, val)

        if con.type == "CHILD_OF":
            con.set_inverse_pending = True

    def _restore_parent_ref(self, bone: bpy.types.PoseBone, bone_ref: dict, info: dict):
        assert self.parent
        assert isinstance(bone_ref, dict)

        arm = self.parent.armature_object
        strategy = bone_ref["strategy"]

        if strategy is None:
            return arm

        assert strategy == "JOINTS"

        joint_head = bone_ref["joint_head"]
        joint_tail = bone_ref["joint_tail"]

        if joint_head and joint_tail and "subtarget" in info:
            head_tail = info.get("head_tail")

            chains, head_tail = self._find_parent_joint_chains_split(joint_head, joint_tail, head_tail)

            bones = self._select_parent_chain_bones(chains, bone.bone.head_local, head_tail)

            if len(bones) > 1:
                org_bones = [item for item in bones if item[0].startswith("ORG-")]
                if org_bones:
                    bones = org_bones

            if len(bones) > 1:
                def_bones = [item for item in bones if arm.pose.bones[item[0]].bone.use_deform]
                if def_bones:
                    bones = def_bones

            if bones:
                bones.sort(key=lambda item: (len(item[2]), item[0]))

                name, head_tail, chain = bones[0]

                info["subtarget"] = name

                if head_tail is not None:
                    info["head_tail"] = head_tail

        return arm

    def _select_parent_chain_bones(self, chains, pos, head_tail):
        """Select the best bone from each chain connecting two joints."""

        single = [(chain[0], head_tail, chain) for chain in chains if len(chain) == 1]

        if single:
            return single

        return [self._select_parent_chain_bone(chain, pos, head_tail) for chain in chains]

    def _select_parent_chain_bone(self, chain, pos, head_tail):
        """Select the best bone from a chain connecting two joints."""

        pose_bones = self.parent.armature_object.pose.bones

        if head_tail is not None:
            # Select bone based on head_tail
            lens = [0, *accumulate(pose_bones[name].bone.length for name in chain)]
            factors = [f / lens[-1] for f in lens]

            for name, fac_cur, fac_next in zip(chain, factors, factors[1:]):
                if fac_cur <= head_tail < fac_next or head_tail == 1 == fac_next:
                    return name, (head_tail - fac_cur) / (fac_next - fac_cur), chain
        else:
            # Select bone based on distance from point
            distances = [(name, self._distance_point_bone(pos, pose_bones[name].bone)) for name in chain]
            distances.sort(key=lambda p: p[1])

            return distances[0][0], None, chain

    @staticmethod
    def _distance_point_bone(point: Vector, bone: bpy.types.Bone):
        """Calculates the distance from a point to a Bone."""
        from mathutils.geometry import intersect_point_line

        closest, fac = intersect_point_line(point, bone.head_local, bone.tail_local)

        if fac < 0:
            closest = bone.head_local
        elif fac > 1:
            closest = bone.tail_local

        return (point - closest).length

    def _find_parent_joint_chains_split(self, joint_head, joint_tail, head_tail):
        """Find chains of bones connecting two joint cubes, with automatic joint unsplitting."""

        def adjust_head_tail(cur_head_tail, head, mid, tail, replace_head):
            if cur_head_tail is not None:
                head_pos = Vector(self.parent.position_info["cubes"][head])
                mid_pos = Vector(self.parent.position_info["cubes"][mid])
                tail_pos = Vector(self.parent.position_info["cubes"][tail])

                len_a = (head_pos - mid_pos).length
                len_b = (tail_pos - mid_pos).length

                if replace_head:
                    return (len_a + cur_head_tail * len_b) / (len_a + len_b)
                else:
                    return cur_head_tail * len_a / (len_a + len_b)

        joint_splits = [
            # The Rigify and Game Engine rigs have only one shoulder bone
            ('joint-l-clavicle', 'joint-l-scapula', 'joint-l-shoulder'),
            ('joint-r-clavicle', 'joint-r-scapula', 'joint-r-shoulder'),
            # The CMU rig doesn't use spine-3
            ('joint-spine-4', 'joint-spine-3', 'joint-spine-2'),
        ]

        chains = self._find_parent_joint_chains(joint_head, joint_tail)

        while not chains:
            for to_head, joint, to_tail in joint_splits:
                if joint == joint_head:
                    head_tail = adjust_head_tail(head_tail, to_head, joint_head, joint_tail, True)
                    joint_head = to_head
                    break
                elif joint == joint_tail:
                    head_tail = adjust_head_tail(head_tail, joint_head, joint_tail, to_tail, False)
                    joint_tail = to_tail
                    break
            else:
                break

            chains = self._find_parent_joint_chains(joint_head, joint_tail)

        return chains, head_tail

    def _find_parent_joint_chains(self, joint_head: str, joint_tail: str):
        """Find chains of bones connecting two joint cubes."""
        chains = []

        for name, bone_info in self.parent.rig_definition.items():
            if bone_info["tail"]["strategy"] == "CUBE" and bone_info["tail"]["cube_name"] == joint_tail:
                chain = []

                cur_bone = self.parent.armature_object.pose.bones[name].bone

                while bone_info := self.parent.rig_definition.get(name):
                    chain.append(name)

                    if bone_info["head"]["strategy"] == "CUBE" and bone_info["head"]["cube_name"] == joint_head:
                        chain.reverse()
                        chains.append(chain)
                        break

                    parent = cur_bone.parent

                    if not parent or (parent.tail_local - cur_bone.head_local).length > _MAX_DIST_TO_CONSIDER_EXACT:
                        break

                    name = parent.name
                    cur_bone = parent

        return chains

    def save_strategies(self, refit=False):
        """Save strategy data in the pose bones for development."""

        from ..ui.boneops import BoneOpsArmatureProperties, BoneOpsBoneProperties
        BoneOpsArmatureProperties.set_value("developer_mode", True, entity_reference=self.armature_object.data)

        for bone_name, bone_info in self.rig_definition.items():
            bone = RigService.find_pose_bone_by_name(bone_name, self.armature_object).bone

            self.assign_bone_end_strategy(bone, bone_info["head"], False)
            self.assign_bone_end_strategy(bone, bone_info["tail"], True)

            if not refit:
                roll_strategy = bone_info.get("roll_strategy", None)
                if roll_strategy:
                    BoneOpsBoneProperties.set_value("roll_strategy", roll_strategy, entity_reference=bone)

    @staticmethod
    def assign_bone_end_strategy(bone, info, is_tail: bool, *, force=False, lock: bool | None=None):
        from ..ui.boneops import BoneOpsBoneProperties, BoneOpsEditBoneProperties

        properties = BoneOpsEditBoneProperties if isinstance(bone, bpy.types.EditBone) else BoneOpsBoneProperties
        prefix = "tail" if is_tail else "head"

        if not force and properties.get_value(prefix + "_strategy_lock", entity_reference=bone):
            return

        if lock is not None:
            properties.set_value(prefix + "_strategy_lock", lock, entity_reference=bone)

        strategy = info["strategy"]

        properties.set_value(prefix + "_strategy", strategy, entity_reference=bone)

        if strategy == "CUBE":
            properties.set_value(prefix + "_cube_name", info["cube_name"], entity_reference=bone)
        elif strategy == "VERTEX":
            properties.set_value(prefix + "_vertex_index", info["vertex_index"], entity_reference=bone)
        elif strategy in ("MEAN", "XYZ"):
            name = properties.get_fullname_key_from_shortname_key(prefix + "_vertex_indices")
            bone[name] = info["vertex_indices"]

        offset = info.get("offset", (0, 0, 0))
        properties.set_value(prefix + "_offset", offset, entity_reference=bone)

    @staticmethod
    def get_bone_end_strategy(bone, is_tail):
        """Retrieve head or tail strategy settings from a bone."""
        from ..ui.boneops import BoneOpsBoneProperties, BoneOpsEditBoneProperties

        properties = BoneOpsEditBoneProperties if isinstance(bone, bpy.types.EditBone) else BoneOpsBoneProperties
        prefix = "tail" if is_tail else "head"

        try:
            force = False
            strategy = properties.get_value(prefix + "_strategy", entity_reference=bone)

            if properties.get_value(prefix + "_strategy_lock", entity_reference=bone):
                force = True

            info = {"strategy": strategy}

            if strategy == "CUBE":
                info["cube_name"] = properties.get_value(prefix + "_cube_name", entity_reference=bone)
            elif strategy == "VERTEX":
                info["vertex_index"] = properties.get_value(prefix + "_vertex_index", entity_reference=bone)
            elif strategy in ("MEAN", "XYZ"):
                name = properties.get_fullname_key_from_shortname_key(prefix + "_vertex_indices")
                info["vertex_indices"] = list(bone.get(name, []))
            else:
                return None, False

            offset = properties.get_value(prefix + "_offset", entity_reference=bone)
            if offset and any(x != 0 for x in offset):
                info["offset"] = list(offset)

            return info, force
        except KeyError:
            return None, False

    def list_unmatched_bones(self):
        """List bones which are still marked as using the DEFAULT positioning strategy."""
        unmatched_bone_names = []

        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]

            if bone_info["head"]["strategy"] == "DEFAULT":
                if not bone_name in unmatched_bone_names:
                    unmatched_bone_names.append(str(bone_name))

            if bone_info["tail"]["strategy"] == "DEFAULT":
                if not bone_name in unmatched_bone_names:
                    unmatched_bone_names.append(str(bone_name))

        return unmatched_bone_names

    def move_basemesh_if_needed(self):
        """Move basemesh so it has feet on ground and apply this transform."""
        self.basemesh.location = (0.0, 0.0, 0.0)
        for vertex in self.basemesh.data.vertices:
            if vertex.co[2] < self.lowest_point and vertex.index < 13380:
                self.lowest_point = vertex.co[2]
        if self.lowest_point < -0.0001:
            self.basemesh.location[2] = abs(self.lowest_point)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    def build_basemesh_position_info(self, take_shape_keys_into_account=True):
        """Populate the position information hash with positions from the base mesh.
        We will here also extract and store vertex positions and store them in the hash,
        as these positions may be influenced by shape keys."""

        self.position_info = dict()

        self.position_info["cubes"] = dict()
        cubes = self.position_info["cubes"]

        self.position_info["vertices"] = []
        vertices = self.position_info["vertices"]

        cube_groups = dict()
        group_index_to_name = dict()

        basemesh: bpy.types.Object = self.basemesh

        assert isinstance(basemesh.data, bpy.types.Mesh)

        if self.parent:
            # Copy cube data from the parent rig if present
            cubes.update(self.parent.position_info["cubes"])
        else:
            # Start computing our own cube data
            for group in basemesh.vertex_groups:
                idx = int(group.index)
                name = str(group.name)
                if "joint" in name:
                    cube_groups[name] = []
                    group_index_to_name[idx] = name

        coords = basemesh.data.vertices
        shape_key = None
        key_name = None

        if take_shape_keys_into_account and basemesh.data.shape_keys and basemesh.data.shape_keys.key_blocks and len(basemesh.data.shape_keys.key_blocks) > 0:
            if basemesh.mode == "EDIT":
                if not basemesh.use_shape_key_edit_mode or basemesh.show_only_shape_key:
                    basemesh.use_shape_key_edit_mode = True
                    basemesh.show_only_shape_key = False
                    bpy.context.view_layer.update()

                bm = bmesh.from_edit_mesh(basemesh.data)
                coords = bm.verts
            else:
                from ..services import TargetService
                key_name = "temporary_fit_rig_key." + str(random.randrange(1000, 9999))
                shape_key = TargetService.create_shape_key(basemesh, key_name, also_create_basis=True, create_from_mix=True)
                coords = shape_key.data

        for vertex in basemesh.data.vertices:
            vertex_coords = list(coords[vertex.index].co)  # Either actual vertex or the corresponding shape key point
            vertices.append(vertex_coords)
            for group in vertex.groups:
                idx = int(group.group)
                if idx in group_index_to_name:
                    name = group_index_to_name[idx]
                    cube_groups[name].append(vertex_coords)

        if shape_key:
            basemesh.shape_key_remove(shape_key)

        _LOG.dump("cube_groups", cube_groups)

        for name in group_index_to_name.values():
            group = cube_groups[name]
            sum_pos = [0.0, 0.0, 0.0]
            for i in range(len(group)):
                for n in range(3):
                    sum_pos[n] = sum_pos[n] + group[i][n]
            for n in range(3):
                sum_pos[n] = sum_pos[n] / float(len(group))
            cubes[name] = sum_pos

    def add_data_bone_info(self):
        """Extract bone information from the bone data."""

        assert self.armature_object.mode != 'EDIT'

        for bone in self.armature_object.data.bones:
            bone_info = dict()
            bone_info["parent"] = ""
            if bone.parent:
                bone_info["parent"] = bone.parent.name

            bone_info["head"] = dict()
            bone_info["head"]["default_position"] = list(bone.head_local)
            bone_info["head"]["strategy"] = "DEFAULT"

            bone_info["tail"] = dict()
            bone_info["tail"]["default_position"] = list(bone.tail_local)
            bone_info["tail"]["strategy"] = "DEFAULT"

            bone_info["use_connect"] = bone.use_connect
            bone_info["use_local_location"] = bone.use_local_location
            bone_info["use_inherit_rotation"] = bone.use_inherit_rotation
            bone_info["inherit_scale"] = bone.inherit_scale

            if bbone_info := self._encode_bbone_info(bone):
                bone_info["bendy_bone"] = bbone_info

            bone_info["collections"] = list(sorted(bcoll.name for bcoll in bone.collections))

            self.rig_definition[bone.name] = bone_info

    def add_edit_bone_info(self):
        """Extract bone information from the edit bones."""

        assert self.armature_object.mode == 'EDIT'

        for bone in self.armature_object.data.edit_bones:
            bone_info = self.rig_definition[bone.name]

            # Info that must be accessed in Edit mode
            bone_info["roll"] = bone.roll

        _LOG.dump("rig_definition after edit bones", self.rig_definition)

    def cleanup_float_values(self):
        """Round some float values in definitions to reduce noise on re-save"""

        # Remove extra digits and negative zero
        clean = lambda val: round(val, 5) + 0

        for name, info in self.rig_definition.items():
            info["head"]["default_position"] = list(map(clean, info["head"]["default_position"]))
            info["tail"]["default_position"] = list(map(clean, info["tail"]["default_position"]))
            if "offset" in info["head"]:
                info["head"]["offset"] = list(map(clean, info["head"]["offset"]))
            if "offset" in info["tail"]:
                info["tail"]["offset"] = list(map(clean, info["tail"]["offset"]))
            info["roll"] = clean(info["roll"])

    def _encode_bbone_info(self, bone):
        defaults = {
            "segments": 1,
            "mapping_mode": "STRAIGHT",
            "custom_handle_start": None, "custom_handle_end": None,
            "handle_type_start": "AUTO", "handle_type_end": "AUTO",
            "handle_use_ease_start": False, "handle_use_ease_end": False,
            "handle_use_scale_start": [False, False, False],
            "handle_use_scale_end": [False, False, False],
            "easein": 1.0, "easeout": 1.0,
        }

        info = {}

        for field, defval in defaults.items():
            val = getattr(bone, "bbone_" + field)

            if field in ("custom_handle_start", "custom_handle_end"):
                val = val.name if val else None
            elif isinstance(val, bpy.types.bpy_prop_array):
                val = list(val)

            if val != defval:
                info[field] = val

        return info

    def add_pose_bone_info(self):
        """Extract information from the pose bones."""

        assert self.armature_object.mode != 'EDIT'

        for bone in self.armature_object.pose.bones:
            bone_info = self.rig_definition[bone.name]

            if bone.rotation_mode != "QUATERNION":
                bone_info["rotation_mode"] = bone.rotation_mode

            if bone.constraints:
                bone_info["constraints"] = [
                    self._encode_constraint_info(bone, con) for con in bone.constraints
                ]

            bone_info["rigify"] = dict()
            rigify = bone_info["rigify"]

            if hasattr(bone, "rigify_parameters") and len(dict(bone.rigify_parameters)) > 0:
                rigify["rigify_parameters"] = dict()
                _LOG.dump("rigify_parameters", dict(bone.rigify_parameters))
                for param in bone.rigify_parameters.keys():
                    param_name = str(param)
                    value = getattr(bone.rigify_parameters, param_name)
                    _LOG.debug("param: ", (param_name, value, type(value)))

                    if isinstance(value, float) or isinstance(value, int) or isinstance(value, str):
                        rigify["rigify_parameters"][param_name] = value
                    elif param_name.endswith("_coll_refs"):
                        rigify["rigify_parameters"][param_name] = [ref.name for ref in value]
                    else:
                        # Assume this is a property array
                        props = []
                        for prop in value:
                            props.append(prop)
                        rigify["rigify_parameters"][param_name] = props

            if hasattr(bone, "rigify_type") and bone.rigify_type:
                rigify["rigify_type"] = str(bone.rigify_type)

    def _encode_constraint_info(self, bone, con):
        info: dict[str, typing.Any] = {
            "type": con.type,
            "name": con.name,
        }

        # Add generic properties
        self._add_constraint_properties(con, info)

        # Handle targets - only support targeting the armature
        if con.type == "ARMATURE":
            targets = info["targets"] = []
            weights = {}

            if self.parent:
                vertex = self.get_armature_constraint_vertex_index(con)
                if vertex is not None:
                    weights = self.parent._find_vertex_weights(vertex)
                    if not weights:
                        self.bad_constraint_targets.add(bone.name)
                    else:
                        info["target"] = {"strategy": "VERTEX", "vertex_index": vertex}

            for tgt in con.targets:
                if weights and tgt.target == self.parent.armature_object:
                    continue

                tgt_info = {"subtarget": tgt.subtarget, "weight": tgt.weight}

                if self.parent and tgt.target == self.parent.armature_object:
                    tgt_info["target"] = self._encode_constraint_parent_ref(bone, tgt.subtarget)
                elif tgt.target != self.armature_object:
                    self.bad_constraint_targets.add(bone.name)
                    continue

                targets.append(tgt_info)
        else:
            target = getattr(con, "target", None)

            if target == self.armature_object:
                info["target"] = True
            elif self.parent and target == self.parent.armature_object:
                info["target"] = self._encode_constraint_parent_ref(bone, getattr(con, "subtarget", None), info)
            else:
                self.bad_constraint_targets.add(bone.name)

        if getattr(con, "space_object", None) == self.armature_object:
            info["space_object"] = True
            info["space_subtarget"] = con.space_subtarget

        return info

    @staticmethod
    def _add_constraint_properties(con, info):
        defaults = {
            'owner_space': 'WORLD', 'target_space': 'WORLD',
            'mute': False, 'influence': 1.0,
        }
        block_props = {
            prop.identifier
            for prop in bpy.types.Constraint.bl_rna.properties
            if prop.identifier not in defaults
        }

        if con.type == "STRETCH_TO":
            # Don't save Stretch To length so it auto-resets when the skeleton is fitted
            block_props.add("rest_length")

        array_types = (bpy.types.bpy_prop_array, Vector, Euler, Quaternion)
        bad_types = (bpy.types.bpy_struct, Matrix)

        for prop in type(con).bl_rna.properties:
            if prop.identifier not in block_props and not prop.is_readonly:
                cur_value = getattr(con, prop.identifier, None)

                if isinstance(cur_value, array_types):
                    value = list(cur_value)

                if prop.identifier in defaults and cur_value == defaults[prop.identifier]:
                    continue

                if not isinstance(cur_value, bad_types):
                    info[prop.identifier] = cur_value

    def _encode_constraint_parent_ref(self, bone, subtarget, info=None):
        if not subtarget:
            return {"strategy": None}

        head_joint, prefix = self.parent._list_parents_until_joint(subtarget)
        tail_joint, suffix = self.parent._list_children_until_joint(subtarget)

        if not head_joint or not tail_joint:
            self.bad_constraint_targets.add(bone.name)
            return {"strategy": None}

        bone_chain = [*prefix, subtarget, *suffix]

        # Recalculate head-tail slider according to the position in the chain
        if len(bone_chain) > 1 and "head_tail" in info:
            pose_bones = self.parent.armature_object.pose.bones

            lens = [0, *accumulate(pose_bones[name].bone.length for name in bone_chain)]
            index = len(prefix)

            info["head_tail"] = lerp(lens[index], lens[index + 1], info["head_tail"]) / lens[-1]

        return {"strategy": "JOINTS", "joint_head": head_joint, "joint_tail": tail_joint}

    def _list_parents_until_joint(self, cur_name):
        bone_info = self.rig_definition.get(cur_name, None)

        if not bone_info:
            return None, []

        if bone_info["head"]["strategy"] == "CUBE":
            return bone_info["head"]["cube_name"], []

        cur_bone = self.armature_object.pose.bones[cur_name]
        parent = cur_bone.parent

        if not parent or (parent.bone.tail_local - cur_bone.bone.head_local).length > _MAX_DIST_TO_CONSIDER_EXACT:
            return None, []

        joint, prefix = self._list_parents_until_joint(parent.name)

        return joint, prefix + [parent.name]

    def _list_children_until_joint(self, cur_name):
        bone_info = self.rig_definition.get(cur_name, None)

        if not bone_info:
            return None, []

        if bone_info["tail"]["strategy"] == "CUBE":
            return bone_info["tail"]["cube_name"], []

        cur_bone = self.armature_object.pose.bones[cur_name].bone
        children = cur_bone.children
        candidates = []

        for child in children:
            if (child.head_local - cur_bone.tail_local).length < _MAX_DIST_TO_CONSIDER_EXACT:
                joint, suffix = self._list_children_until_joint(child.name)
                if joint:
                    candidates.append((joint, [child.name] + suffix))

        if not candidates:
            return None, []

        joint, suffix = sorted(candidates, key=lambda x: len(x[1]))[0]
        return joint, suffix

    def _find_vertex_weights(self, vertex):
        """Retrieve deform weights associated with the given mesh vertex."""

        mesh_obj: bpy.types.Object = self.basemesh
        mesh = mesh_obj.data
        assert isinstance(mesh, bpy.types.Mesh)

        def_bones = set(RigService.get_deform_group_bones(self.armature_object))
        weights = {}

        if 0 <= vertex < len(mesh.vertices):
            vertex_groups = mesh_obj.vertex_groups

            for group in mesh.vertices[vertex].groups:
                if 0 <= group.group < len(vertex_groups):
                    name = vertex_groups[group.group].name
                    if name in def_bones:
                        weights[name] = group.weight

        return weights

    def match_bone_positions_with_strategies(self, fast=False):
        """Try to find out bone positions matching joint cubes."""

        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]

            self._match_position_to_strategy(bone_info["head"], fast)
            self._match_position_to_strategy(bone_info["tail"], fast)

    def _match_position_to_strategy(self, position_info, fast):
        pos = position_info["default_position"]

        best_dist = 100.0
        exact_threshold = _MAX_DIST_TO_CONSIDER_EXACT
        strategy = None

        cube_name, cube_dist = self.find_closest_cube(pos)
        vertex_idx, vertex_dist = self.find_closest_vertex(pos)

        if cube_name is not None:
            strategy = "CUBE"
            best_dist = cube_dist

        if vertex_idx is not None:
            # Prefer exact vertex to a non-exact cube
            if not strategy or vertex_dist < exact_threshold < cube_dist:
                strategy = "VERTEX"
                best_dist = vertex_dist

        # Use mean to replace non-exact vertices if better
        if strategy != "CUBE" and best_dist > exact_threshold and not fast:
            # If already near a vertex, only search for a better mean nearby.
            search_radius = CLOSE_MEAN_SEARCH_RADIUS if strategy else None

            mean_idxs, mean_dist = self.find_closest_vertex_mean(pos, search_radius=search_radius)

            if mean_idxs is not None and mean_dist < best_dist:
                strategy = "MEAN"
                position_info["vertex_indices"] = mean_idxs

        if strategy:
            position_info["strategy"] = strategy

            if strategy == "CUBE":
                position_info["cube_name"] = cube_name
            elif strategy == "VERTEX":
                position_info["vertex_index"] = vertex_idx

    def restore_saved_strategies(self):
        """Check if the saved strategies are better and apply them."""

        for bone in self.armature_object.data.bones:
            bone_info = self.rig_definition[bone.name]

            roll_strategy = bone.get("mpfb_roll_strategy", None)
            if roll_strategy:
                bone_info["roll_strategy"] = roll_strategy

                # Clear roll if it will be overwritten
                if roll_strategy in ("ALIGN_Z_WORLD_Z", "ALIGN_X_WORLD_X"):
                    bone_info["roll"] = 0.0

            self._restore_end_strategy(bone, bone_info, False)
            self._restore_end_strategy(bone, bone_info, True)

    def get_bone_strategy_and_location(self, bone, is_tail):
        info, _force = self.get_bone_end_strategy(bone, is_tail)
        pos = None

        if info:
            pos = self.get_best_location_from_strategy(info, use_default=False)

        return info, pos

    def _restore_end_strategy(self, bone, bone_info, is_tail):
        field = "tail" if is_tail else "head"
        saved_head, force = self.get_bone_end_strategy(bone, is_tail)

        if saved_head:
            cur_head = bone_info[field]
            true_pos = cur_head["default_position"]
            saved_pos = self.get_best_location_from_strategy(saved_head, use_default=False)

            if not saved_pos:
                return

            if not force:
                cur_pos = self.get_best_location_from_strategy(cur_head, use_default=False)

                if cur_pos:
                    # If the saved strategy is not worse, use it
                    cur_dist = self._distance(true_pos, cur_pos)
                    saved_dist = self._distance(true_pos, saved_pos)

                    if saved_dist - cur_dist > _STRATEGY_REPLACE_THRESHOLD:
                        return

            saved_head["default_position"] = true_pos
            bone_info[field] = saved_head

    def _distance(self, pos1, pos2):
        if pos1 is None:
            raise ValueError("Pos 1 in _distance is None")

        if pos2 is None:
            raise ValueError("Pos 2 in _distance is None")

        if len(pos1) != 3:
            _LOG.error("Malformed pos 1", pos1)
            raise ValueError("Pos 1 is not an array with three values")

        if len(pos2) != 3:
            _LOG.error("Malformed pos 2", pos2)
            raise ValueError("Pos 2 is not an array with three values")

        sqr_pos = [0.0, 0.0, 0.0]

        for i in range(3):
            sqr_pos[i] = abs(pos1[i] - pos2[i]) * abs(pos1[i] - pos2[i])
        return math.sqrt(sqr_pos[0] + sqr_pos[1] + sqr_pos[2])

    def _get_cube_tree(self):
        if "cubes_tree" in self.position_info:
            return self.position_info["cubes_tree"], self.position_info["cubes_list"]

        cubes = self.position_info["cubes"]

        if not cubes:
            return None, None

        cube_list = self.position_info["cubes_list"] = list(cubes.keys())
        cube_tree = self.position_info["cubes_tree"] = KDTree(len(cube_list))

        for i, name in enumerate(cube_list):
            cube_tree.insert(cubes[name], i)

        cube_tree.balance()

        return cube_tree, cube_list

    def find_closest_cube(self, pos, max_allowed_dist: float | None=_MAX_ALLOWED_DIST
                          ) -> tuple[str, float] | tuple[None, None]:
        cube_tree, cube_list = self._get_cube_tree()

        if not cube_tree:
            return None, None

        # Find the closest point
        _cube_pos, index, dist = cube_tree.find(pos)

        if max_allowed_dist is None or dist < max_allowed_dist:
            return cube_list[index], dist

        return None, None

    def _get_vertex_tree(self):
        if "vertices_tree" in self.position_info:
            return self.position_info["vertices_tree"]

        vertices = self.position_info["vertices"]

        assert len(vertices) > 0

        vertex_tree = self.position_info["vertices_tree"] = KDTree(len(vertices))

        for i, vert in enumerate(vertices):
            vertex_tree.insert(vert, i)

        vertex_tree.balance()

        return vertex_tree

    def find_closest_vertex(self, pos, max_allowed_dist: float | None=_MAX_ALLOWED_DIST
                            ) -> tuple[int, float] | tuple[None, None]:
        vertex_tree = self._get_vertex_tree()

        # Find the closest point
        _vertex, idx, dist = vertex_tree.find(pos)

        if max_allowed_dist is None or dist < max_allowed_dist:
            return idx, dist

        return None, None

    def _get_vertex_total_height(self):
        if "vertices_mean_scale" in self.position_info:
            return self.position_info["vertices_mean_scale"]

        vertices = self.position_info["vertices"]

        highest_z = -1000.0
        lowest_z = 1000.0

        for vertex in vertices:
            if vertex[2] > highest_z:
                highest_z = vertex[2]
            if vertex[2] < lowest_z:
                lowest_z = vertex[2]

        total_height = abs(highest_z - lowest_z)
        _LOG.debug("total height", total_height)

        self.position_info["vertices_mean_scale"] = total_height

        return total_height

    def find_closest_vertex_mean(self, pos, max_allowed_dist=_MAX_ALLOWED_DIST * 2, search_radius=None):
        vertex_tree = self._get_vertex_tree()

        # Only include verts which are less than 15% of the total height
        # away from the position along any axis.
        max_axis_distance = 0.15 * self._get_vertex_total_height()

        if search_radius is None:
            search_radius = max_axis_distance

        # Factor used to penalize longer matches without much precision benefit.
        # At _MEAN_LENGTH_PENALTY an exact vertex pair at max_axis_distance is the
        # same weight as a zero distance pair with mean at max_allowed_dist.
        length_penalty = _MEAN_LENGTH_PENALTY * max_allowed_dist / (max_axis_distance * 2)

        pos = Vector(pos)

        best_match_weight = max_allowed_dist + length_penalty * max_axis_distance * 2
        best_match_idxs = None
        best_match_dist = max_allowed_dist

        # Loop over vertices anywhere within max_axis_distance along any axis.
        for vertex1, idx1, dist1 in vertex_tree.find_range(pos, search_radius * math.sqrt(3)):
            # Check against the cube for better backward compatibility.
            if max(map(abs, vertex1 - pos)) >= search_radius:
                continue

            # Finding a vertex pair with mean closest to the center is mathematically the same as
            # finding a second vertex closest to the location of the first one mirrored against center.
            vertex2, idx2, dist2 = vertex_tree.find(pos * 2 - vertex1)

            # Only check one symmetry order, since [idx1, idx2] and [idx2, idx1] are equivalent.
            if idx2 <= idx1:
                continue

            # Compute and check the mean.
            mean = (vertex1 + vertex2) / 2
            dist = (mean - pos).magnitude

            if dist < max_allowed_dist:
                # Compute an abstract weight to penalize more distant pairs.
                weight = dist + (vertex2 - vertex1).magnitude * length_penalty

                if weight < best_match_weight:
                    best_match_weight = weight
                    best_match_idxs = [idx1, idx2]
                    best_match_dist = dist

        return best_match_idxs, best_match_dist


def matrix_from_axis_pair(y_axis, other_axis, axis_name):
    assert axis_name in 'xz'

    y_axis = Vector(y_axis).normalized()

    if axis_name == 'x':
        z_axis = Vector(other_axis).cross(y_axis).normalized()
        x_axis = y_axis.cross(z_axis)
    else:
        x_axis = y_axis.cross(other_axis).normalized()
        z_axis = x_axis.cross(y_axis)

    return Matrix((x_axis, y_axis, z_axis)).transposed()
