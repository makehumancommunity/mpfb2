"""Contains a class for cross-referencing data in a mesh."""

import numpy, time, mathutils, os
from mpfb.services.meshservice import MeshService
from mpfb.services.objectservice import ObjectService
from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("entities.meshcrossref")

# Possible calculation TODOs:
# - Faces by edge
# - Edges by face
# - UV..
# - Texco...

class MeshCrossRef:
    """
    A container for various cross references inside a mesh, for example listing faces a vertex belongs to.

    The built tables for coordinates, verts, edges and faces are all 2d numpy arrays:
    - vertex_coordinates: row number is vertex index and columns are x,y,z coordinates
    - vertices_by_face: row number is face index and columns are vertex indices
    - vertices_by_edge: row number is edge index and columns are vertex indices
    - vertices_by_group: row number is group index and columns are vertex indices
    - faces_by_vertex: row number is vertex index and columns are face indices
    - edges_by_vertex: row number is vertex index and columns are edge indices
    - face_neighbors: row number is face index and columns are neighbor face indices
    - face_median_points: row number is face index and columns are x,y,z coordinates of the median point of the face
    - face_normals: row number is face index and columns are x,y,z coordinates of the normal shifted by the median point

    There are also KDTree objects for some tables:
    - vertex_coordinates_kdtree: KDTree of vertex_coordinates
    - face_median_points_kdtree: KDTree of face_median_points

    Additionally, there are reference tables for vertex groups:
    - group_index_to_group_name: list where position is group index and value is group name
    - group_name_to_group_index: dict where key is group name and value is group index
    - vertices_without_group: list with vertex indices of vertices which are not in any group
    - vertices_without_group: list with vertex indices of vertices which are not in any group
    - vertices_with_multiple_groups: list with vertex indices of vertices which are in more than one group
    - faces_by_group: Row number is group index, cols is a list of face indices where at least three verts belong to the group.

    The faces_by_group table takes a long time to build, so it is optional (set the build_faces_by_group_reference parameter to build it).
    """

    def __init__(self, mesh_object, after_modifiers=True, build_faces_by_group_reference=False, cache_dir=None, write_cache=False, read_cache=False, world_coordinates=True):
        _LOG.enter()

        self._mesh_object = mesh_object

        self.cache_dir = cache_dir
        self.write_cache = write_cache
        self.read_cache = read_cache
        self.world_coordinates = world_coordinates

        if cache_dir:
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)

        # Cannot have modifiers which alter the number of vertices
        if after_modifiers:
            _stripped_mesh_object = mesh_object.copy()
            _stripped_mesh_object.data = mesh_object.data.copy()
            ObjectService.link_blender_object(_stripped_mesh_object)
            for modifier in _stripped_mesh_object.modifiers:
                if modifier.type in ["MASK", "SUBSURF"]:
                    _stripped_mesh_object.modifiers.remove(modifier)
            self._mesh_object = _stripped_mesh_object

        self.vertex_coordinates = MeshService.get_vertex_coordinates_as_numpy_array(self._mesh_object, after_modifiers=after_modifiers)
        self.vertex_coordinates_kdtree = MeshService.get_kdtree(self._mesh_object, after_modifiers=after_modifiers)
        self.vertices_by_face = MeshService.get_faces_as_numpy_array(self._mesh_object)
        self.vertices_by_edge = MeshService.get_edges_as_numpy_array(self._mesh_object)

        before = int(time.time() * 1000.0)
        self.faces_by_vertex = []
        self._build_faces_by_vertex_table()
        after = int(time.time() * 1000.0)
        _LOG.debug("Building faces_by_vertex table took", (after - before))

        before = int(time.time() * 1000.0)
        self.edges_by_vertex = []
        self._build_edges_by_vertex_table()
        after = int(time.time() * 1000.0)
        _LOG.debug("Building edges_by_vertex table took", (after - before))

        before = int(time.time() * 1000.0)
        self.face_neighbors = []
        self._build_face_neighbors_table()
        after = int(time.time() * 1000.0)
        _LOG.debug("Building face_neighbors table took", (after - before))

        before = int(time.time() * 1000.0)
        self.face_median_points = []
        self.face_normals = []
        self.face_median_points_kdtree = None
        self._build_face_median_points_table()
        after = int(time.time() * 1000.0)
        _LOG.debug("Building face_median_points and face_normals tables took", (after - before))

        before = int(time.time() * 1000.0)
        self.group_index_to_group_name = []
        self.group_name_to_group_index = dict()
        self.vertices_by_group = []
        self._potential_faces_by_group = []
        self.vertices_without_group = []
        self.vertices_with_multiple_groups = []
        self._build_vert_group_references(build_faces_by_group_reference=build_faces_by_group_reference)
        after = int(time.time() * 1000.0)
        _LOG.debug("Building vert_group_references took", (after - before))

        if build_faces_by_group_reference:
            before = int(time.time() * 1000.0)
            self.faces_by_group = []
            self._build_faces_by_group_table()
            after = int(time.time() * 1000.0)
            _LOG.debug("Building faces_by_group took", (after - before))

        if after_modifiers:
            ObjectService.delete_object(self._mesh_object)

        self._mesh_object = None

    def read_array_from_cache(self, cache_file_name):
        _LOG.enter()
        if not self.cache_dir or not self.read_cache:
            _LOG.trace("Cache directory or read_cache is not set")
            return None
        if not os.path.exists(self.cache_dir):
            _LOG.trace("Cache dir does not exist", self.cache_dir)
            return None

        absolute_file_path = os.path.abspath(os.path.join(self.cache_dir, cache_file_name))

        if not os.path.exists(absolute_file_path):
            _LOG.trace("Cache file does not exist", absolute_file_path)
            return None

        cached_array = numpy.load(absolute_file_path)
        _LOG.debug("Loaded cached array from", (absolute_file_path, type(cached_array)))
        return cached_array

    def write_array_to_cache(self, cache_file_name, numpy_array):
        _LOG.enter()
        if not self.cache_dir or not self.write_cache:
            _LOG.trace("Cache directory or write_cache is not set")
            return
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        absolute_file_path = os.path.abspath(os.path.join(self.cache_dir, cache_file_name))

        if os.path.exists(absolute_file_path):
            _LOG.debug("Removing stale cache file", absolute_file_path)
            os.remove(absolute_file_path)

        numpy.save(absolute_file_path, numpy_array)

        _LOG.debug("Wrote cache file", (absolute_file_path, type(numpy_array)))


    def _build_vert_group_references(self, build_faces_by_group_reference=False):
        _LOG.enter()
        vert_by_group = []
        vertices_without_group = []
        vertices_with_multiple_groups = []

        WITHOUT_FILE = "vertices_without_group.npy"
        MULTIPLE_FILE = "vertices_with_multiple_groups.npy"
        VERTS_BY_GROUP = "vertices_by_group_%d.npy"
        FACES_BY_GROUP = "faces_by_group_%d.npy"

        required_cache_files = [WITHOUT_FILE, MULTIPLE_FILE]

        for group_idx in range(len(self._mesh_object.vertex_groups)):
            group = self._mesh_object.vertex_groups[group_idx]
            if group_idx != group.index:
                raise ValueError("Vertex groups must be in linear order")
            self.group_name_to_group_index[group.name] = group.index
            self.group_index_to_group_name.append(group.name)
            vert_by_group.append([])
            if build_faces_by_group_reference:
                self._potential_faces_by_group.append([])
            required_cache_files.append(VERTS_BY_GROUP % group_idx)
            required_cache_files.append(FACES_BY_GROUP % group_idx)

        able_to_read_from_cache = (self.cache_dir is not None) and self.read_cache
        if able_to_read_from_cache:
            for fn in required_cache_files:
                if not os.path.exists(os.path.join(self.cache_dir, fn)):
                    _LOG.debug("Cannot read from cache since at least one of the required cache files does not exist", fn)
                    able_to_read_from_cache = False
                    break

        if able_to_read_from_cache:
            _LOG.debug("All cache files exist, and reading from cache is enabled")
            self.vertices_without_group = self.read_array_from_cache(WITHOUT_FILE)
            self.vertices_with_multiple_groups = self.read_array_from_cache(MULTIPLE_FILE)
            for group_idx in range(len(self._mesh_object.vertex_groups)):
                self.vertices_by_group.append(self.read_array_from_cache(VERTS_BY_GROUP % group_idx))
            return

        for vertex in self._mesh_object.data.vertices:
            for group in vertex.groups:
                vert_by_group[group.group].append(vertex.index)
                if build_faces_by_group_reference:
                    vertex_found_at_2d = numpy.argwhere(self.vertices_by_face == vertex.index) # Returns 2d array where col 1 is face number and 2 is position in face
                    if len(vertex_found_at_2d) > 0:
                        vertex_found_at = vertex_found_at_2d[:,0] # Extract col 1, ie the face number
                        _LOG.trace("Vertex, faces", (vertex.index, vertex_found_at, list(vertex_found_at)))
                        self._potential_faces_by_group[group.group].extend(list(vertex_found_at))
            if len(vertex.groups) < 1:
                vertices_without_group.append(vertex.index)
            if len(vertex.groups) > 1:
                vertices_with_multiple_groups.append(vertex.index)
        for groupverts in vert_by_group:
            self.vertices_by_group.append(numpy.sort(numpy.unique(numpy.array(groupverts, dtype=numpy.uint32))))

        self.vertices_without_group = numpy.sort(numpy.unique(numpy.array(vertices_without_group)))
        self.vertices_with_multiple_groups = numpy.sort(numpy.unique(numpy.array(vertices_with_multiple_groups)))

        self.write_array_to_cache(WITHOUT_FILE, self.vertices_without_group)
        self.write_array_to_cache(MULTIPLE_FILE, self.vertices_with_multiple_groups)

        for group_idx in range(len(self._mesh_object.vertex_groups)):
            self.write_array_to_cache(VERTS_BY_GROUP % group_idx, self.vertices_by_group[group_idx])


    def _build_faces_by_group_table(self):
        _LOG.enter()
        for group_idx in range(len(self.vertices_by_group)):
            group_name = self.group_index_to_group_name[group_idx]
            cache_file_name = "faces_by_group_%d.npy" % group_idx
            faces_in_group = self.read_array_from_cache(cache_file_name)
            if faces_in_group is not None:
                self.faces_by_group.append(faces_in_group)
            else:
                potential_faces_in_group = numpy.unique(numpy.array(self._potential_faces_by_group[group_idx], dtype=numpy.uint32))
                _LOG.trace("Potential faces in group", (group_idx, len(potential_faces_in_group)))
                faces_in_group = []
                group_verts = self.vertices_by_group[group_idx]
                for face_idx in potential_faces_in_group:
                    face_verts = self.vertices_by_face[face_idx]
                    mask = numpy.isin(face_verts, group_verts, assume_unique=True)
                    _LOG.trace("Is in", (face_idx, mask, face_verts[mask]))
                    if len(face_verts[mask]) >= 3:
                        faces_in_group.append(face_idx)
                faces_in_group = numpy.sort(numpy.unique(numpy.array(faces_in_group, dtype=numpy.uint32)))
                self.write_array_to_cache(cache_file_name, faces_in_group)
                self.faces_by_group.append(faces_in_group)
            _LOG.debug("Group contains faces", (group_name, len(faces_in_group)))

    def _build_faces_by_vertex_table(self):
        _LOG.enter()

        cache_file = None
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, "faces_by_vertex.npy")
            if self.read_cache and os.path.exists(cache_file):
                _LOG.debug("Reading from cache", cache_file)
                self.faces_by_vertex = numpy.load(cache_file, allow_pickle=True)
                return

        faces_by_vertex = []

        for i in range(len(self.vertex_coordinates)):
            vertex_found_at_2d = numpy.argwhere(self.vertices_by_face == i) # Returns 2d array where col 1 is face number and 2 is position in face
            if len(vertex_found_at_2d) > 0:
                vertex_found_at = vertex_found_at_2d[:,0] # Extract col 1, ie the face number
                _LOG.trace("Vertex, faces", (i, vertex_found_at))
                faces_by_vertex.append(numpy.unique(vertex_found_at))
            else:
                faces_by_vertex.append(numpy.array([]))

        self.faces_by_vertex = numpy.array(faces_by_vertex, dtype=object)
        if self.write_cache and self.cache_dir:
            if os.path.exists(cache_file):
                os.remove(cache_file)
            _LOG.debug("Writing to cache", cache_file)
            numpy.save(cache_file, self.faces_by_vertex, allow_pickle=True)


    def _build_edges_by_vertex_table(self):
        _LOG.enter()

        cache_file = None
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, "edges_by_vertex.npy")
            if self.read_cache and os.path.exists(cache_file):
                _LOG.debug("Reading from cache", cache_file)
                self.edges_by_vertex = numpy.load(cache_file, allow_pickle=True)
                return

        edges_by_vertex = []

        for i in range(len(self.vertex_coordinates)):
            vertex_found_at_2d = numpy.argwhere(self.vertices_by_edge == i) # Returns 2d array where col 1 is edge number and 2 is position in edge
            if len(vertex_found_at_2d) > 0:
                vertex_found_at = vertex_found_at_2d[:,0] # Extract col 1, ie the edge number
                _LOG.trace("Vertex, edges", (i, vertex_found_at))
                edges_by_vertex.append(numpy.unique(vertex_found_at))
            else:
                edges_by_vertex.append(numpy.array([]))

        self.edges_by_vertex = numpy.array(edges_by_vertex, dtype=object)
        if self.write_cache and self.cache_dir:
            if os.path.exists(cache_file):
                os.remove(cache_file)
            _LOG.debug("Writing to cache", cache_file)
            numpy.save(cache_file, self.edges_by_vertex, allow_pickle=True)

    def _build_face_neighbors_table(self):
        _LOG.enter()

        cache_file = None
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, "face_neighbors.npy")
            if self.read_cache and os.path.exists(cache_file):
                _LOG.debug("Reading from cache", cache_file)
                self.face_neighbors = numpy.load(cache_file, allow_pickle=True)
                return

        face_neighbors = []

        for face_idx in range(len(self.vertices_by_face)):
            found_faces = numpy.array([], dtype=numpy.uint32)
            for vert_idx in self.vertices_by_face[face_idx]:
                found_faces = numpy.append(found_faces, self.faces_by_vertex[vert_idx])
            found_faces = numpy.unique(found_faces)
            to_remove = numpy.isin(found_faces, [face_idx])
            found_faces = numpy.delete(found_faces, to_remove)
            face_neighbors.append(found_faces)
            _LOG.trace("Face neighbors", (face_idx, found_faces))

        self.face_neighbors = numpy.array(face_neighbors, dtype=object)
        if self.write_cache and self.cache_dir:
            if os.path.exists(cache_file):
                os.remove(cache_file)
            _LOG.debug("Writing to cache", cache_file)
            numpy.save(cache_file, self.face_neighbors, allow_pickle=True)


    def _build_face_median_points_table(self):
        _LOG.enter()
        kd = mathutils.kdtree.KDTree(len(self.vertices_by_face))
        for face_idx in range(len(self.vertices_by_face)):
            numverts = len(self.vertices_by_face[face_idx])
            vert_table = numpy.zeros((numverts, 3), dtype=numpy.float32)
            i = 0;
            for vert_idx in self.vertices_by_face[face_idx]:
                vert_table[i] = self.vertex_coordinates[vert_idx]
                i = i + 1
            median_point = numpy.mean(vert_table, axis=0)
            normal_raw = numpy.array(self._mesh_object.data.polygons[face_idx].normal, dtype=numpy.float32)
            normal_shifted = numpy.add(normal_raw, median_point)
            _LOG.trace("Face vert table", (face_idx, numverts, vert_table, median_point, normal_shifted))
            self.face_normals.append(normal_shifted)
            self.face_median_points.append(median_point)
            kd.insert(list(median_point), face_idx)
        kd.balance()
        self.face_median_points_kdtree = kd
