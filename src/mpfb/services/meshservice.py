"""Utility functions for working with meshes"""

import bpy, mathutils, numpy
from mathutils import Vector
from .logservice import LogService
from .objectservice import ObjectService

_LOG = LogService.get_logger("services.meshservice")
_LOG.set_level(LogService.DEBUG)


class MeshService:
    """The MeshService class is a utility class designed to provide various functions for working with meshes, vertex groups, weights,
    and related operations in Blender. It is structured to offer a collection of static methods that facilitate the creation,
    manipulation, and querying of mesh data. The class is not intended to be instantiated; instead, its static methods should be used directly.

    Its key responsibilities are:

    - Mesh creation
    - Vertex group management
    - Handling of spatial data structures (KDTree)
    - Data extraction (getting mesh info as numpy structures)
    - Various utility methods

    Note that some mesh operations are also available in ObjectService, for example loading wavefront files."""

    def __init__(self):
        raise RuntimeError("You should not instance MeshService. Use its static methods instead.")

    @staticmethod
    def create_mesh_object(vertices, edges, faces, vertex_groups=None, name="sample_object", link=True):
        """
        Create a new mesh object from given vertices, edges, and faces, and optionally assign vertex groups.

        Parameters:
        - vertices: A list of vertex coordinates.
        - edges: A list of edges, where each edge is defined by a pair of vertex indices.
        - faces: A list of faces, where each face is defined by a list of vertex indices.
        - vertex_groups: A dictionary where keys are group names and values are lists of [vertex index, weight] pairs.
        - name: The name of the new mesh object.
        - link: Whether to link the new object to the current Blender scene.

        Returns:
        - The created mesh object.
        """
        target_mesh = bpy.data.meshes.new(name + "_mesh")
        target_mesh.from_pydata(vertices, edges, faces)
        target_object = bpy.data.objects.new(name, target_mesh)
        if vertex_groups:
            for key in vertex_groups.keys():
                MeshService.create_vertex_group(target_object, str(key), vertex_groups[key], nuke_existing_group=True)
        if link:
            ObjectService.link_blender_object(target_object)
        return target_object

    @staticmethod
    def create_sample_object(name="sample_object", link=True):
        """Create a sample plane mesh with four faces."""
        #  0   1   2
        #  3   4   5
        #  6   7   8

        vertices = [
            (-1, 0, 1),  #  0
            (0, 0, 1),  #  1
            (1, 0, 1),  #  2
            (-1, 0, 0),  #  3
            (0, 0, 0),  #  4
            (1, 0, 0),  #  5
            (-1, 0, -1),  #  6
            (0, 0, -1),  #  7
            (1, 0, -1)  #  8
            ]

        edges = []

        faces = [
            (0, 1, 4, 3),
            (1, 2, 5, 4),
            (3, 4, 7, 6),
            (4, 5, 8, 7)
            ]

        vgroups = {
            "left": [],
            "right": [],
            "mid": [],
            "all": []
            }

        for i in [0, 1, 3, 4, 6, 7]:
            vgroups["left"].append([i, 1.0])

        for i in [2, 2, 4, 5, 7, 8]:
            vgroups["right"].append([i, 1.0])

        for i in [1, 4, 7]:
            vgroups["mid"].append([i, 1.0])

        for i in range(9):
            vgroups["all"].append([i, 1.0])

        return MeshService.create_mesh_object(vertices, edges, faces, vertex_groups=vgroups, name=name, link=link)

    @staticmethod
    def find_vertices_in_vertex_group(mesh_object, vertex_group_name):
        """Find all vertices in a vertex group, return a list with vertex index and weight in group."""
        _LOG.enter()
        result = []

        vertex_group = mesh_object.vertex_groups.get(vertex_group_name)
        if not vertex_group:
            return result

        for vert in mesh_object.data.vertices:
            for group in vert.groups:
                if group.group == vertex_group.index:
                    result.append([vert.index, group.weight])

        return result

    @staticmethod
    def find_faces_in_vertex_group(mesh_object, vertex_group_name):
        """
        Find all faces where all vertices are in the given vertex group.

        Parameters:
        - mesh_object: The mesh object to find faces in.
        - vertex_group_name: The name of the vertex group to check.

        Returns:
        - A list of face indices where all vertices are in the given vertex group.
        """
        _LOG.enter()
        result = []

        vertex_group = mesh_object.vertex_groups.get(vertex_group_name)
        if not vertex_group:
            return result

        for face in mesh_object.data.polygons:
            all_vertices_belong_to_group = True
            for vertex_index in face.vertices:
                vertex = mesh_object.data.vertices[vertex_index]
                if vertex_group.index not in [group.group for group in vertex.groups]:
                    all_vertices_belong_to_group = False
                    break
            if all_vertices_belong_to_group:
                result.append(face.index)

        _LOG.debug("Found {} faces in vertex group {}".format(len(result), vertex_group_name))

        return result

    @staticmethod
    def get_uv_map_names(mesh_object):
        """List all UV map names in the mesh object."""
        _LOG.enter()
        return [uv_map.name for uv_map in mesh_object.data.uv_layers]

    @staticmethod
    def get_uv_map_as_dict(mesh_object, uv_map_name, only_include_vertex_group=None):
        """
        Return a dict where the key is the face index and the value is a dict where the key is the loop index and the value the uv coordinates.
        Optionally only include faces where all vertices are in the given vertex group.

        Parameters:
        - mesh_object: The mesh object to get the UV map from.
        - uv_map_name: The name of the UV map to get.
        - only_include_vertex_group: The name of the vertex group to check. If not provided, all faces will be included.

        Returns:
        - A dict where the key is the face index and the value is a dict where the key is the loop index and the value the uv coordinates.
        """
        _LOG.enter()
        uv_map = mesh_object.data.uv_layers.get(uv_map_name)
        if not uv_map:
            _LOG.debug("UV map not found in mesh object", uv_map_name)
            return {}

        _LOG.debug("UV map, UV map data, UV map data length", (uv_map, uv_map.data, len(uv_map.data)))

        faces_to_include = []
        if only_include_vertex_group:
            faces_to_include = MeshService.find_faces_in_vertex_group(mesh_object, only_include_vertex_group)
        else:
            for face in mesh_object.data.polygons:
                faces_to_include.append(face.index)

        result = {}

        for face_index in faces_to_include:
            _LOG.debug("Getting UV map for face", face_index)
            face_uvs = {}
            for loop_index in mesh_object.data.polygons[face_index].loop_indices:
                _LOG.debug("-- loop_index", loop_index)
                uv = uv_map.data[loop_index].uv
                face_uvs[loop_index] = [uv[0], uv[1]]
            result[face_index] = face_uvs

        return result

    @staticmethod
    def add_uv_map_from_dict(mesh_object, uv_map_name, uv_map_as_dict):
        """
        Create a new UV map from a given dict and add it to the mesh object. If an UV map with the same name already exists, it will be replaced.
        Otherwise, it will be created with the given name.

        Parameters:
        - mesh_object: The mesh object on which to add the UV map.
        - uv_map_name: The name of the new UV map.
        - uv_map_as_dict: A dict where the key is the face index and the value is a dict where the key is the loop index and the value the uv coordinates.
        """
        _LOG.enter()
        _LOG.debug("Adding UV map from dict", {"mesh_object": mesh_object,
                                                 "uv_map_name": uv_map_name,
                                                 "uv_map_as_dict": uv_map_as_dict})
        uv_map = mesh_object.data.uv_layers.get(uv_map_name)
        if uv_map:
            _LOG.debug("Replacing existing UV map", {"uv_map_name": uv_map_name})
            mesh_object.data.uv_layers.remove(uv_map)
            uv_map = None

        uv_map = mesh_object.data.uv_layers.new(name=uv_map_name, do_init=False)

        for face_index, uv_info in uv_map_as_dict.items():
            for loop_index, uv_coords in uv_info.items():
                _LOG.debug("Setting UV coords", {
                    "face_index": face_index,
                    "loop_index": loop_index,
                    "uv_coords": uv_coords})

                uv_map.data[int(loop_index)].uv = uv_coords

    @staticmethod
    def create_vertex_group(mesh_object, vertex_group_name, verts_and_weights, nuke_existing_group=False):
        """Create a new vertex group and add verts and weights to it."""
        _LOG.enter()
        _LOG.debug("Creating new vertex group", {"mesh_object": mesh_object,
                                                 "vertex_group_name": vertex_group_name,
                                                 "verts_and_weights": verts_and_weights,
                                                 "nuke_existing_group": nuke_existing_group})
        group = mesh_object.vertex_groups.get(vertex_group_name)
        _LOG.debug("Existing vertex group", group)

        if group and nuke_existing_group:
            mesh_object.vertex_groups.remove(group)
            group = None

        if not group:
            group = mesh_object.vertex_groups.new(name=vertex_group_name)

        _LOG.debug("Final group", group)

        for index, weight in verts_and_weights:
            group.add([index], weight, 'REPLACE')

    @staticmethod
    def get_kdtree(mesh_object, balance=True, limit_to_vertex_group=None, after_modifiers=False, world_coordinates=True):
        """
        Get a kdtree from a mesh object.

        Parameters:
        - mesh_object: The mesh object to get the kdtree from.
        - balance: Whether to balance the kdtree.
        - limit_to_vertex_group: The name of the vertex group to limit the kdtree to.

        Returns: A kdtree."""
        _LOG.enter()

        mesh = mesh_object.data

        if after_modifiers:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated_mesh = mesh_object.evaluated_get(depsgraph)
            mesh = evaluated_mesh.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

        size = len(mesh.vertices)

        _LOG.debug("Getting kdtree", {
            "mesh_object": mesh_object,
            "mesh": mesh,
            "size": size,
            "balance": balance,
            "limit_to_vertex_group": limit_to_vertex_group
            })

        kd = mathutils.kdtree.KDTree(size)

        if not limit_to_vertex_group:
            for i, v in enumerate(mesh.vertices):
                coord = v.co
                if world_coordinates:
                    coord = mesh_object.matrix_world @ coord
                kd.insert(coord, i)
        else:
            group_index = None
            for group in mesh_object.vertex_groups:
                if group.name == limit_to_vertex_group:
                    group_index = group.index
                    break
            if group_index is None:
                raise ValueError("Cannot find vertex group with name: {}".format(limit_to_vertex_group))
            for vert in mesh.vertices:
                for group in vert.groups:
                    if group.group == group_index:
                        kd.insert(vert.co, vert.index)
        if balance:
            kd.balance()

        if after_modifiers:
            evaluated_mesh.to_mesh_clear()

        return kd

    @staticmethod
    def closest_vertices(focus_obj, focus_vert_idx, target_obj, target_obj_kdtree, number_of_matches=1, world_coordinates=True):
        """
        For a given vertex on the focus object, find the closest vertex/vertices on the target object.

        Parameters:
        - focus_obj: The object that has the vertex we want to find a something close to.
        - focus_vert_idx: The index of the vertex we want to find a something close to.
        - target_obj: The object that has vertices that might be close to the focus vertex.
        - target_obj_kdtree: The kdtree of the target object.
        - number_of_matches: The number of closest matches to return, defaults to 1.

        Returns: A list with vertex indices of the closest matches.
        """
        if not focus_obj or not target_obj:
            raise ValueError("Cannot operate on null objects.")
        if not target_obj_kdtree:
            raise ValueError("Cannot operate on null kdtree.")

        fake_scale = Vector((1.0, 1.0, 1.0))
        if (focus_obj.scale - fake_scale).length > 0.0001:
            raise ValueError("Cannot operate on objects with different scales.")
        if (target_obj.scale - fake_scale).length > 0.0001:
            raise ValueError("Cannot operate on objects with different scales.")

        vert = focus_obj.data.vertices[focus_vert_idx]
        coord = Vector(vert.co)
        if world_coordinates:
            coord = focus_obj.matrix_world @ coord

        # shift_dist = focus_obj.location - target_obj.location
        # if shift_dist.length > 0.0001:
        #    coord.x = coord.x - shift_dist.x
        #    coord.y = coord.y - shift_dist.y
        #    coord.z = coord.z - shift_dist.z

        if number_of_matches == 1:
            return [target_obj_kdtree.find(coord)]

        return target_obj_kdtree.find_n(coord, number_of_matches)

    @staticmethod
    def get_vertex_coordinates_as_numpy_array(mesh_object, after_modifiers=False, world_coordinates=True):
        """Get the vertex coordinates as a numpy array where the vertex index is the row number."""

        _LOG.enter()

        mesh = mesh_object.data

        if after_modifiers:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated_mesh = mesh_object.evaluated_get(depsgraph)
            mesh = evaluated_mesh.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

        size = len(mesh.vertices)

        vert_array = numpy.zeros((size, 3), dtype=numpy.float32)
        for i, v in enumerate(mesh.vertices):
            coord = v.co
            if world_coordinates:
                coord = mesh_object.matrix_world @ coord
            for axis in range(3):
                vert_array[i][axis] = float(coord[axis])

        if after_modifiers:
            evaluated_mesh.to_mesh_clear()

        return vert_array

    @staticmethod
    def get_faces_as_numpy_array(mesh_object):
        """Get the faces as a numpy array."""

        _LOG.enter()
        mesh = mesh_object.data
        size = len(mesh.polygons)

        verts_per_face = None

        for face in mesh.polygons:
            if not verts_per_face:
                verts_per_face = len(face.vertices)
            if len(face.vertices) != verts_per_face:
                raise ValueError("Faces must have the same number of vertices. Found both {} and {}".format(len(face.vertices), verts_per_face))

        face_array = numpy.zeros((size, verts_per_face), dtype=numpy.uint32)
        for face in mesh.polygons:
            for v in range(verts_per_face):
                face_array[face.index][v] = face.vertices[v]

        return face_array

    @staticmethod
    def get_edges_as_numpy_array(mesh_object):
        """Get the edges as a numpy array."""

        _LOG.enter()
        mesh = mesh_object.data
        size = len(mesh.edges)

        verts_per_edge = None

        # This is most likely unnecessary
        for edge in mesh.edges:
            if not verts_per_edge:
                verts_per_edge = len(edge.vertices)
            if len(edge.vertices) != verts_per_edge:
                raise ValueError("Edges must have the same number of vertices. Found both {} and {}".format(len(edge.vertices), verts_per_edge))

        edge_array = numpy.zeros((size, verts_per_edge), dtype=numpy.uint32)
        for edge in mesh.edges:
            for v in range(verts_per_edge):
                edge_array[edge.index][v] = edge.vertices[v]

        return edge_array

    @staticmethod
    def get_mesh_cross_references(mesh_object, after_modifiers=True, build_faces_by_group_reference=False):
        """Build a cross reference container for the mesh object."""
        _LOG.enter()
        from ..entities.meshcrossref import MeshCrossRef
        return MeshCrossRef(mesh_object, after_modifiers=after_modifiers, build_faces_by_group_reference=build_faces_by_group_reference)

    @staticmethod
    def select_all_vertices_in_vertex_group_for_active_object(vertex_group_name, deselect_other=True):
        """Select all vertices in a specific vertex group for the currently active object.
        The object needs to be active."""
        _LOG.enter()

        mesh_object = bpy.context.active_object
        _LOG.debug("Active object", mesh_object)

        bpy.ops.mesh.select_mode(type="VERT")
        if deselect_other:
            bpy.ops.mesh.select_all(action='DESELECT')

        if vertex_group_name:
            for group in mesh_object.vertex_groups:
                if group.name == vertex_group_name:
                    mesh_object.vertex_groups.active_index = group.index

            bpy.ops.object.vertex_group_select()
