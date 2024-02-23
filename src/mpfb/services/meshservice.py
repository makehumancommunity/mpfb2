import bpy, mathutils, numpy
from mathutils import Vector
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService

_LOG = LogService.get_logger("services.meshservice")

# Possible TODOs:
# - create mesh
# - add numpy array as verts to bmesh
# - add numpy array as faces to bmesh
# - create vertex group
# - add verts to vertex group
# - delete verts in vertex group
# - delete verts
# - recalculate_face_normals

class MeshService:
    """MeshService contains various functions for working meshes, vertex groups, weights and similar."""

    def __init__(self):
        raise RuntimeError("You should not instance MeshService. Use its static methods instead.")

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

        #shift_dist = focus_obj.location - target_obj.location
        #if shift_dist.length > 0.0001:
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
            for d in range(3):
                vert_array[i][d] = float(coord[d])

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
        for edge in mesh.polygons:
            for v in range(verts_per_edge):
                edge_array[edge.index][v] = edge.vertices[v]

        return edge_array

    @staticmethod
    def get_mesh_cross_references(mesh_object, after_modifiers=True, build_faces_by_group_reference=False):
        """Build a cross reference container for the mesh object."""
        _LOG.enter()
        from mpfb.entities.meshcrossref import MeshCrossRef
        return MeshCrossRef(mesh_object, after_modifiers=after_modifiers, build_faces_by_group_reference=build_faces_by_group_reference)




