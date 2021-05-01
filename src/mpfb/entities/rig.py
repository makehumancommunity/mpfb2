"""This module contains functionality for serializing/deserializing rigs via JSON."""

from mpfb.services.logservice import LogService
from mpfb.services.rigservice import RigService
from mpfb.entities.objectproperties import GeneralObjectProperties
import bpy, math, json, random

_LOG = LogService.get_logger("entities.rig")

_MAX_ALLOWED_DIST = 0.01
_MAX_DIST_TO_CONSIDER_EXACT = 0.001

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

        return rig

    def create_armature_and_fit_to_basemesh(self):
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

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        modifier = self.basemesh.modifiers.new("Armature", 'ARMATURE')
        modifier.object = self.armature_object
        while self.basemesh.modifiers.find(modifier.name) != 0:
            bpy.ops.object.modifier_move_up({'object': self.basemesh}, modifier=modifier.name)

        return self.armature_object

    def _get_best_location_from_strategy(self, head_or_tail_info):
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
            vertex1 = self.position_info["vertices"][indices[0]]
            vertex2 = self.position_info["vertices"][indices[1]]
            location = [0.0, 0.0, 0.0]
            for i in range(3):
                location[i] = (vertex1[i] + vertex2[i]) / 2
        if location is None:
            location = head_or_tail_info["default_position"]
        return location

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
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def reposition_edit_bone(self):
        """Reposition bones to fit the current state of the basemesh."""
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]
            bone = RigService.find_edit_bone_by_name(bone_name, self.armature_object)
            bone.head = self._get_best_location_from_strategy(bone_info["head"])
            bone.tail = self._get_best_location_from_strategy(bone_info["tail"])
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
                i = 0
                for layer in bone_info["layers"]:
                    bone.layers[i] = layer
                    i = i + 1

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def rigify_metadata(self):
        """Assign bone meta data fitting for the pose bones."""
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for bone_name in self.rig_definition.keys():
            bone_info = self.rig_definition[bone_name]["rigify"]
            bone = RigService.find_pose_bone_by_name(bone_name, self.armature_object)

            if "rigify_type" in bone_info and bone_info["rigify_type"]:
                bone.rigify_type = bone_info["rigify_type"]

            if "rigify_parameters" in bone_info:
                for key in bone_info["rigify_parameters"].keys():
                    value = bone_info["rigify_parameters"][key]
                    if isinstance(value, list):
                        pass
                    else:
                        _LOG.debug("Will attempt to set bone.parameters.", key)
                        setattr(bone.rigify_parameters, str(key), value)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

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
        We will here also extract and stor vertex positions and store them in the hash,
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

            bone_info["layers"] = []
            for layer in bone.layers:
                bone_info["layers"].append(layer)

            self.rig_definition[bone.name] = bone_info

        _LOG.dump("rig_definition after edit bones", self.rig_definition)

    def add_pose_bone_info(self):
        """Extract information from the pose bones."""

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        for bone in self.armature_object.pose.bones:
            bone_info = self.rig_definition[bone.name]
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
