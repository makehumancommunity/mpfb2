import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService

_LOG = LogService.get_logger("services.meshservice")

# create mesh

# add numpy array as verts to bmesh
# add numpy array as faces to bmesh

# get verts as numpy array
# get vertex groups
# create vertex group
# add verts to vertex group
# verts in vertex group
# delete verts in vertex group
# delete verts

# recalculate_face_normals


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
