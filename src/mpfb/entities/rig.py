"""This module contains functionality for serializing/deserializing rigs via JSON."""

from mpfb.services.logservice import LogService
from mpfb.services.rigservice import RigService
from mpfb.entities.objectproperties import GeneralObjectProperties

import bpy, math, json, random

from mathutils import Vector, Matrix

_LOG = LogService.get_logger("entities.rig")

_MAX_ALLOWED_DIST = 0.01
_MAX_DIST_TO_CONSIDER_EXACT = 0.001
_STRATEGY_REPLACE_THRESHOLD = 0.0001

class Rig:

    """Entity class representing an armature."""

    def __init__(self):
        """You might want to use one of the static methods rather than calling init directly."""
        self.basemesh = None
        self.armature_object = None
        self.position_info = dict()
        self.rig_definition = dict()
        self.lowest_point = 1000.0

    @staticmethod
    def from_json_file_and_basemesh(filename, basemesh):
        """Create an instance of Rig and populate it with information from the json file and from the base mesh."""
        rig = Rig()
        with open(filename, "r") as json_file:
            rig.rig_definition = json.load(json_file)
        rig.basemesh = basemesh
        rig.build_basemesh_position_info()
        return rig

    @staticmethod
    def from_given_basemesh_and_armature_as_active_object(basemesh):
        """Create an instance of Rig and populate it with information from the base mesh
        and from the armature which is expected to be the currently active object."""

        rig = Rig()

        rig.armature_object = bpy.context.object
        rig.basemesh = basemesh
        rig.build_basemesh_position_info()
        rig.add_edit_bone_info()
        rig.add_pose_bone_info()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        rig.match_edit_bones_with_joint_cubes()
        rig.match_remaining_edit_bones_with_vertices()
        rig.match_remaining_edit_bones_with_vertex_means()
        rig.restore_saved_strategies()

        return rig

    def create_armature_and_fit_to_basemesh(self, for_developer=False, preserve_volume=False):
        """Use the information in the object to construct an armature and adjust it to fit the base mesh."""

        #self.move_basemesh_if_needed()

        bpy.ops.object.armature_add(location=self.basemesh.location)
        self.armature_object = bpy.context.object

        scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=self.basemesh)
        GeneralObjectProperties.set_value("scale_factor", scale_factor, entity_reference=self.armature_object)
        GeneralObjectProperties.set_value("object_type", "Skeleton", entity_reference=self.armature_object)

        self.armature_object.show_in_front = True
        self.armature_object.data.display_type = 'WIRE'

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        for bone in self.armature_object.data.edit_bones:
            self.armature_object.data.edit_bones.remove(bone)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False) # To commit removal of bones

        self.create_bones()
        self.update_edit_bone_metadata()
        self.rigify_metadata()

        if for_developer:
            self.save_strategies()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        modifier = self.basemesh.modifiers.new("Armature", 'ARMATURE')
        modifier.object = self.armature_object
        modifier.use_deform_preserve_volume = preserve_volume
        while self.basemesh.modifiers.find(modifier.name) != 0:
            bpy.ops.object.modifier_move_up({'object': self.basemesh}, modifier=modifier.name)

        return self.armature_object

    def _get_best_location_from_strategy(self, head_or_tail_info, use_default=True):
        strategy = head_or_tail_info["strategy"]
        location = None
        if strategy == "CUBE":
            name = head_or_tail_info["cube_name"]
            location = self.position_info["cubes"][name]
        if strategy == "VERTEX":
            index = head_or_tail_info["vertex_index"]
            location = self.position_info["vertices"][index]
        if strategy == "MEAN":
            indices = head_or_tail_info["vertex_indices"]
            vertices = [self.position_info["vertices"][i] for i in indices]
            location = [sum(v[i] for v in vertices)/len(vertices) for i in range(3)]
        if strategy == "XYZ":
            # Special strategy for Rigify heel marker.
            # Uses different vertices for each coordinate channel.
            indices = head_or_tail_info["vertex_indices"]
            vertices = [self.position_info["vertices"][i] for i in indices]
            location = [vertices[i][i] for i in range(3)]
        if location is None and use_default:
            location = head_or_tail_info["default_position"]
        return location

    def _align_roll_by_strategy(self, bone, bone_info):
        roll_strategy = bone_info.get("roll_strategy", None)
        matrix = None

        if roll_strategy == "ALIGN_Z_WORLD_Z":
            matrix = matrix_from_axis_pair(bone.y_axis, (0,0,1), 'z')

        if matrix:
            bone.roll = bpy.types.Bone.AxisRollFromMatrix(matrix, axis=bone.y_axis)[1]

    def create_bones(self):
        """Create the actual bones in the armature object."""
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bones = self.armature_object.data.edit_bones
        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]
            bone = bones.new(bone_name)
            bone.roll = bone_info["roll"]
            bone.head = self._get_best_location_from_strategy(bone_info["head"])
            bone.tail = self._get_best_location_from_strategy(bone_info["tail"])

            self._align_roll_by_strategy(bone, bone_info)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def reposition_edit_bone(self):
        """Reposition bones to fit the current state of the basemesh."""
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]
            bone = RigService.find_edit_bone_by_name(bone_name, self.armature_object)
            if bone:
                bone.head = self._get_best_location_from_strategy(bone_info["head"])
                bone.tail = self._get_best_location_from_strategy(bone_info["tail"])
            else:
                _LOG.warn("Tried to refit bone that did not exist in definition", bone_name)
                _LOG.debug("Bone info is", bone_info)
                _LOG.dump("Rig definition is", self.rig_definition)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

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
            if "layers" in bone_info:

                # Mask layers to allow deselection
                i = 0
                for layer in bone_info["layers"]:
                    bone.layers[i] = True
                    i = i + 1

                i = 0
                for layer in bone_info["layers"]:
                    bone.layers[i] = layer
                    i = i + 1

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
                    try:
                        setattr(bone.rigify_parameters, str(key), value)
                    except AttributeError:
                        _LOG.error("Rigify bone parameter not found.", key)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _apply_constraint_info(self, bone, info):
        con = bone.constraints.new(info["type"])

        if con.type == "ARMATURE":
            for tgt_info in info["targets"]:
                tgt = con.targets.new()
                tgt.target = self.armature_object
                tgt.subtarget = tgt_info["subtarget"]
                tgt.weight = tgt_info["weight"]
        elif info.get("target", False):
            con.target = self.armature_object

        if info.get("space_object", False):
            con.space_object = self.armature_object

        skip_list = {"type", "targets", "target", "space_object"}

        for field, val in info.items():
            if field not in skip_list:
                setattr(con, field, val)

    def save_strategies(self):
        """Save strategy data in the pose bones for development."""

        for bone_name, bone_info in self.rig_definition.items():
            bone = RigService.find_pose_bone_by_name(bone_name, self.armature_object).bone

            self._save_end_strategy(bone, bone_info["head"], "mpfb_head")
            self._save_end_strategy(bone, bone_info["tail"], "mpfb_tail")

            roll_strategy = bone_info.get("roll_strategy", None)
            if roll_strategy:
                bone["mpfb_roll_strategy"] = roll_strategy

    def _save_end_strategy(self, bone, info, prefix):
        strategy = info["strategy"]

        if strategy == "CUBE":
            bone[prefix + "_cube_name"] = info["cube_name"]
        elif strategy == "VERTEX":
            bone[prefix + "_vertex_index"] = info["vertex_index"]
        elif strategy in ("MEAN", "XYZ"):
            bone[prefix + "_vertex_indices"] = info["vertex_indices"]
        else:
            return

        bone[prefix + "_strategy"] = strategy

    def _get_end_strategy(self, bone, prefix):
        """Retrieve head or tail strategy settings from a bone."""
        try:
            force = False
            strategy = bone[prefix + "_strategy"]

            # Allow using e.g. "!CUBE" to override the distance check
            if strategy[0] == '!':
                strategy = strategy[1:]
                force = True

            info = { "strategy": strategy }

            if strategy == "CUBE":
                info["cube_name"] = bone[prefix + "_cube_name"]
            elif strategy == "VERTEX":
                info["vertex_index"] = bone[prefix + "_vertex_index"]
            elif strategy in ("MEAN", "XYZ"):
                info["vertex_indices"] = list(bone[prefix + "_vertex_indices"])
            else:
                return None, False

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

        basemesh = self.basemesh

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
            from mpfb.services.targetservice import TargetService
            key_name = "temporary_fit_rig_key." + str(random.randrange(1000, 9999))
            shape_key = TargetService.create_shape_key(basemesh, key_name, also_create_basis=True, create_from_mix=True)
            coords = shape_key.data

        for vertex in basemesh.data.vertices:
            vertex_coords = list(coords[vertex.index].co) # Either actual vertex or the corresponding shape key point
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

    def add_edit_bone_info(self):
        """Extract bone information from the edit bones."""

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        for bone in self.armature_object.data.edit_bones:
            bone_info = dict()
            bone_info["parent"] = ""
            if bone.parent:
                bone_info["parent"] = bone.parent.name

            bone_info["head"] = dict()
            bone_info["head"]["default_position"] = list(bone.head)
            bone_info["head"]["strategy"] = "DEFAULT"

            bone_info["tail"] = dict()
            bone_info["tail"]["default_position"] = list(bone.tail)
            bone_info["tail"]["strategy"] = "DEFAULT"

            bone_info["roll"] = bone.roll
            bone_info["use_connect"] = bone.use_connect
            bone_info["use_local_location"] = bone.use_local_location
            bone_info["use_inherit_rotation"] = bone.use_inherit_rotation
            bone_info["inherit_scale"] = bone.inherit_scale

            if bone.bbone_segments > 1:
                bone_info["bendy_bone"] = self._encode_bbone_info(bone)

            bone_info["layers"] = []
            for layer in bone.layers:
                bone_info["layers"].append(layer)

            self.rig_definition[bone.name] = bone_info

        _LOG.dump("rig_definition after edit bones", self.rig_definition)

    def _encode_bbone_info(self, bone):
        defaults = {
            "segments": 1,
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

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        for bone in self.armature_object.pose.bones:
            bone_info = self.rig_definition[bone.name]

            if bone.rotation_mode != "QUATERNION":
                bone_info["rotation_mode"] = bone.rotation_mode

            if bone.constraints:
                bone_info["constraints"] = [
                    self._encode_constraint_info(con) for con in bone.constraints
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
                    else:
                        # Assume this is a property array
                        props = []
                        for prop in value:
                            props.append(prop)
                        rigify["rigify_parameters"][param_name] = props

            if hasattr(bone, "rigify_type") and bone.rigify_type:
                rigify["rigify_type"] = str(bone.rigify_type)

    def _encode_constraint_info(self, con):
        info = {
            "type": con.type,
            "name": con.name,
        }

        # Handle targets - only support targeting the armature
        if con.type == "ARMATURE":
            info["targets"] = [
                { "subtarget": tgt.subtarget, "weight": tgt.weight }
                for tgt in con.targets if tgt.target == self.armature_object
            ]
        elif getattr(con, "target", None) == self.armature_object:
            info["target"] = True

        if getattr(con, "space_object", None) == self.armature_object:
            info["space_object"] = True
            info["space_subtarget"] = con.space_subtarget

        # Add other properties
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

        for prop in type(con).bl_rna.properties:
            if prop.identifier not in block_props and not prop.is_readonly:
                cur_value = getattr(con, prop.identifier, None)

                if isinstance(cur_value, bpy.types.bpy_prop_array):
                    value = list(cur_value)

                if prop.identifier in defaults and cur_value == defaults[prop.identifier]:
                    continue

                if not isinstance(cur_value, bpy.types.bpy_struct):
                    info[prop.identifier] = cur_value

        return info

    def match_edit_bones_with_joint_cubes(self):
        """Try to find out bone positions matching joint cubes."""

        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]

            head_cube_name = self._find_closest_cube(bone_info["head"]["default_position"])
            tail_cube_name = self._find_closest_cube(bone_info["tail"]["default_position"])

            if head_cube_name and not head_cube_name is None:
                bone_info["head"]["strategy"] = "CUBE"
                bone_info["head"]["cube_name"] = head_cube_name

            if tail_cube_name and not tail_cube_name is None:
                bone_info["tail"]["strategy"] = "CUBE"
                bone_info["tail"]["cube_name"] = tail_cube_name

    def match_remaining_edit_bones_with_vertices(self):
        """Go through all bones and try to match the one with DEFAULT strategy against vertex positions."""

        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]

            if bone_info["head"]["strategy"] != "CUBE":
                head_vertex_index = self._find_closest_vertex(bone_info["head"]["default_position"])
                if not head_vertex_index is None:
                    bone_info["head"]["strategy"] = "VERTEX"
                    bone_info["head"]["vertex_index"] = head_vertex_index

            if bone_info["tail"]["strategy"] != "CUBE":
                tail_vertex_index = self._find_closest_vertex(bone_info["tail"]["default_position"])
                if not tail_vertex_index is None:
                    bone_info["tail"]["strategy"] = "VERTEX"
                    bone_info["tail"]["vertex_index"] = tail_vertex_index

    def match_remaining_edit_bones_with_vertex_means(self):
        """Go through all bones and try to match the one with DEFAULT strategy against geometric means between vertex positions."""

        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]

            if bone_info["head"]["strategy"] == "DEFAULT":
                _LOG.debug("Starting to look for mean for head", (bone_name, bone_info["head"]["default_position"]))
                head_vertex_indices = self._find_closest_vertex_mean(bone_info["head"]["default_position"])
                if not head_vertex_indices is None:
                    bone_info["head"]["strategy"] = "MEAN"
                    bone_info["head"]["vertex_indices"] = head_vertex_indices

            if bone_info["tail"]["strategy"] == "DEFAULT":
                _LOG.debug("Starting to look for mean for tail", (bone_name, bone_info["tail"]["default_position"]))
                tail_vertex_indices = self._find_closest_vertex_mean(bone_info["tail"]["default_position"])
                if not tail_vertex_indices is None:
                    bone_info["tail"]["strategy"] = "MEAN"
                    bone_info["tail"]["vertex_indices"] = tail_vertex_indices

    def restore_saved_strategies(self):
        """Check if the saved strategies are better and apply them."""

        for bone in self.armature_object.data.bones:
            bone_info = self.rig_definition[bone.name]

            roll_strategy = bone.get("mpfb_roll_strategy", None)
            if roll_strategy:
                bone_info["roll_strategy"] = roll_strategy

                # Clear roll if it will be overwritten
                if roll_strategy in ("ALIGN_Z_WORLD_Z"):
                    bone_info["roll"] = 0.0

            self._restore_end_strategy(bone, bone_info, "head")
            self._restore_end_strategy(bone, bone_info, "tail")

    def _restore_end_strategy(self, bone, bone_info, field):
        saved_head, force = self._get_end_strategy(bone, "mpfb_" + field)

        if saved_head:
            cur_head = bone_info[field]
            true_pos = cur_head["default_position"]
            saved_pos = self._get_best_location_from_strategy(saved_head, use_default=False)

            if not saved_pos:
                return

            if not force:
                cur_pos = self._get_best_location_from_strategy(cur_head, use_default=False)

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
            sqr_pos[i] = abs(pos1[i]-pos2[i]) * abs(pos1[i]-pos2[i])
        return math.sqrt(sqr_pos[0] + sqr_pos[1] + sqr_pos[2])

    def _find_closest_cube(self, pos, max_allowed_dist=_MAX_ALLOWED_DIST, max_dist_to_consider_exact=_MAX_DIST_TO_CONSIDER_EXACT):
        cubes = self.position_info["cubes"]

        best_match_name = None
        best_match_dist = 1000.0

        for name in cubes.keys():
            cube_pos = cubes[name]
            dist = self._distance(pos, cube_pos)
            if dist < max_dist_to_consider_exact:
                # This position is so close to the center of the cube that we consider it an exact match
                return str(name)
            if dist < best_match_dist:
                best_match_name = str(name)
                best_match_dist = dist

        if best_match_dist < max_allowed_dist:
            return best_match_name

        return None

    def _find_closest_vertex(self, pos, max_allowed_dist=_MAX_ALLOWED_DIST, max_dist_to_consider_exact=_MAX_DIST_TO_CONSIDER_EXACT):

        best_match_index = None
        best_match_dist = 1000.0

        # There's no point in calculating exact distances to vertices which are rougly, more than 0.1 points
        # away from the desired position
        reasonably_close_vertices = []
        max_allowed_distsum = max_allowed_dist * 10

        # Make a first sweep to see if we can find an exact match. Three subtractions is a lot faster
        # than calculating a distance with square roots and whatnot.
        for idx in range(len(self.position_info["vertices"])):
            vertex = self.position_info["vertices"][idx]
            is_close = True
            distsum = 0.0
            for i in range(3):
                dist = abs(vertex[i] - pos[i])
                if dist > max_dist_to_consider_exact:
                    is_close = False
                distsum = distsum + dist
            if is_close:
                # We found a vertex which is close enough to be considered an exact match
                return idx
            if distsum < max_allowed_distsum:
                # The vertext is close enough to be relevant to consider when calculating
                # exact distances
                reasonably_close_vertices.append(idx)

        # We did not have an exact match. Make secondary sweep

        for idx in reasonably_close_vertices:
            vertex = self.position_info["vertices"][idx]
            dist = self._distance(pos, vertex)
            if dist < best_match_dist:
                best_match_dist = dist
                best_match_index = idx

        if best_match_dist < max_allowed_dist:
            return best_match_index

        return None

    def _find_closest_vertex_mean(self, pos, max_allowed_dist=_MAX_ALLOWED_DIST*2, max_dist_to_consider_exact=_MAX_DIST_TO_CONSIDER_EXACT*2):

        within_range_idxs = []

        # First we'll only include verts which are less than 15% of the total height
        # away from the position along any axis

        highest_z = -1000.0
        lowest_z = 1000.0

        for idx in range(len(self.position_info["vertices"])):
            vertex = self.position_info["vertices"][idx]
            if vertex[2] > highest_z:
                highest_z = vertex[2]
            if vertex[2] < lowest_z:
                lowest_z = vertex[2]

        total_height = abs(highest_z - lowest_z)
        _LOG.debug("total height", total_height)

        max_axis_distance = 0.15 * total_height

        for idx in range(len(self.position_info["vertices"])):
            vertex = self.position_info["vertices"][idx]
            is_close = True
            for i in range(3):
                if abs(pos[i] - vertex[i]) > max_axis_distance:
                    is_close = False
            if is_close:
                # This vertex is close enough to be considered at all
                within_range_idxs.append(idx)

        geometric_means_table = dict()

        # The geometric mean should be even closer
        max_allowed_distsum = max_axis_distance / 5

        for idx1 in within_range_idxs:
            geometric_means_table[idx1] = dict()
            vertex1 = self.position_info["vertices"][idx1]
            for idx2 in within_range_idxs:
                vertex2 = self.position_info["vertices"][idx2]
                distsum = 0.0
                vertex_mean = [0.0, 0.0, 0.0]
                for i in range(3):
                    vertex_mean[i] = (vertex1[i] + vertex2[i]) / 2.0
                    distsum = distsum + abs(pos[i] - vertex_mean[i])
                if distsum < (max_dist_to_consider_exact * 3):
                    # This is a candidate to check early
                    actual_dist = self._distance(pos, vertex_mean)
                    if actual_dist < max_dist_to_consider_exact:
                        return [idx1, idx2]
                if distsum < max_allowed_distsum:
                    geometric_means_table[idx1][idx2] = vertex_mean

        # Within all reason we should already have found a match. But if we haven't, there's no recourse
        # short of brute forcing the entire table

        best_match_idxs = None
        best_match_dist = 1000.0

        for idx1 in within_range_idxs:
            for idx2 in within_range_idxs:
                if idx1 in geometric_means_table and idx2 in geometric_means_table[idx1]:
                    vertex_mean = geometric_means_table[idx1][idx2]
                    dist = self._distance(pos, vertex_mean)
                    if dist < max_dist_to_consider_exact:
                        return [idx1, idx2]
                    if dist < best_match_dist and dist < max_allowed_dist:
                        best_match_dist = dist
                        best_match_idxs = [idx1, idx2]

        return best_match_idxs


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
