"""Functionality for matching one clothes vertex against relevant basemesh vertices"""

import time

from mpfb.services.meshservice import MeshService
from mpfb.services.logservice import LogService

from mathutils import Vector
import mathutils

_LOG = LogService.get_logger("entities.vertexmatch")

class VertexMatch:
    def __init__(self, focus_obj, focus_vert_index, focus_crossref, target_obj, target_crossref, scale_factor=1.0, reference_scale=None):
        """Construct a VertexMatch object.

        Parameters:
        - focus_obj: The clothes/bodypart type object to work with
        - focus_vert_index: The index of the clothes/bodypart vertex that needs to be matched against the basemesh type object
        - focus_crossref: The clothes/bodypart type object MesshCrossRef to work with
        - target_crossref: The basemesh type object MesshCrossRef to work with

        Note that the focus/target objects can be any mesh objects, not necessarily just clothes or basemesh. The parameters
        describe the conceptual intended use.
        """
        _LOG.enter()
        self.focus_obj = focus_obj
        self.focus_vert_index = focus_vert_index
        self.focus_crossref = focus_crossref
        self.target_obj = target_obj
        self.target_crossref = target_crossref
        self.scale_factor = scale_factor
        self.reference_scale = reference_scale

        self.focus_vert_coord = self.focus_crossref.vertex_coordinates[self.focus_vert_index]
        self.focus_vert_group_name = None

        self.best_three_verts = None
        self.mhclo_line = None

        for group_idx in range(len(self.focus_crossref.group_index_to_group_name)):
            if focus_vert_index in self.focus_crossref.vertices_by_group[group_idx]:
                self.focus_vert_group_name = self.focus_crossref.group_index_to_group_name[group_idx]

        if not self.focus_vert_group_name:
            raise ValueError("Vertex %d is not part of any group" % focus_vert_index)

        _LOG.trace("======================== VERTEX MATCH START ========================")

        _LOG.trace("Vert info", {
            "focus_vert_index": self.focus_vert_index,
            "focus_vert_coord": self.focus_vert_coord,
            "focus_vert_group_name": self.focus_vert_group_name
            })

        self.target_group_idx = None
        if self.focus_vert_group_name in self.target_crossref.group_name_to_group_index:
            self.target_group_idx = self.target_crossref.group_name_to_group_index[self.focus_vert_group_name]
        else:
            raise ValueError("Vertex group %s does not exist on target" % self.focus_vert_group_name)

        before = time.time()

        self.final_strategy = None

        self.exact_match_index = None
        self.exact_match_coord = None

        _LOG.trace("------------------------ Exact match strategy ------------------------")
        self._attempt_exact_match()

        if not self.final_strategy:
            _LOG.trace("------------------------ Simple face strategy ------------------------")
            self._attempt_simple_face_match()
        if not self.final_strategy:
            _LOG.trace("------------------------ Extended face strategy ------------------------")
            self._attempt_extended_face_match()
        if not self.final_strategy:
            raise ValueError("Could not match vertex", focus_vert_index)

        _LOG.trace("======================== VERTEX MATCH SUMMARY ========================")

        after = time.time()
        duration = int((after - before) * 1000.0)
        _LOG.debug("Entire matching procedure took %d ms" % duration)
        _LOG.debug("Final strategy", self.final_strategy)

        _LOG.trace("======================== VERTEX MATCH END ========================")

    def _distance(self, focus_vert, target_vert):
        # TODO: adjust coord for world space locations of focus object vs target object
        fvec = Vector(list(focus_vert))
        tvec = Vector(list(target_vert))
        return (fvec - tvec).length

    def _bake_best_verts_match(self, all_potential_verts):

        if len(all_potential_verts) < 3:
            raise ValueError("Not enough potential vertices to pick from")

        fcoord = self.focus_vert_coord
        selected_verts = list(all_potential_verts)

        while len(selected_verts) > 3:
            furthest_dist = -1
            furthest_idx = -1
            for vert in all_potential_verts:
                tcoord = self.target_crossref.vertex_coordinates[vert]
                dist = self._distance(fcoord, tcoord)
                if dist > furthest_dist:
                    furthest_dist = dist
                    furthest_idx = vert
            if furthest_idx == -1:
                raise ValueError("Could not find closest vertex to %s" % str(fcoord))
            selected_verts.remove(furthest_idx)

        # For now, use the original MC2 calculations:
        self._legacy_bake(selected_verts)
        #self._alternative_bake(selected_verts)

    def _legacy_bake(self, selected_verts):
        # While this is the "understandable" version, it is completely incomprehensible to most people
        # It should be rewritten with at least readable variable named and comments which explains the
        # reasoning in layman terms. The comments below are the ones that came from the original MC2

        # To make the algorithm understandable I change our 3 vertices to triangle ABC and use Blender
        # Vectors to be able to use internal functions like cross, dot, normal whatever you need
        # For all vectors I use only capital letters, reading is simplified imho
        mhclo_line = dict()

        vidxa = selected_verts[0]
        vidxb = selected_verts[1]
        vidxc = selected_verts[2]

        mhclo_line["verts"] = [vidxa, vidxb, vidxc]

        coorda = self.target_crossref.vertex_coordinates[vidxa]
        coordb = self.target_crossref.vertex_coordinates[vidxb]
        coordc = self.target_crossref.vertex_coordinates[vidxc]

        A = Vector(coorda)
        B = Vector(coordb)
        C = Vector(coordc)

        # The vertex on the clothes is the Vector Q
        Q = Vector(self.focus_vert_coord)

        # We need the normal for this triangle. Normally it is calculated with cross-product using the
        # distance of e.g. B-A and C-A, but blender has a function implemented for that

        N= mathutils.geometry.normal (A, B, C)
        # print ("normal vector is " + str(N))

        # transform normal vector to corner of triangle and recalculate length
        # new vector is R (direction is the same)
        QA = Q - A
        R = Q - N * QA.dot(N)

        # now weight the triangle multiplied with the normal
        #
        BA = B-A
        BA.normalize()
        NBA = N.cross(BA)
        NBA.normalize()

        AC = A-C
        BC = B-C
        RC = R-C

        # we are using barycentric coordinates to determine the weights. Normally you have
        # to do a projection. To get the values of all dimensions we can use the scalar or dot.product
        # of our vectors. This is also called projection product ...
        # the barycentric calculation now could be rewritten as
        #
        # WeightA = ( BC.NBA * RC.BA - BC.BA * RC.NBA) / (BA.AC * BC.NBA - BC.AC * AC.NBA)
        # WeightB = (-AC.NBA * RC.BA + AC.BA * RC.NBA) / (BA.AC * BC.NBA - BC.AC * AC.NBA)
        #
        # WeightC = 1 - WeightA - WeightB

        a00 = AC.dot(BA)
        a01 = BC.dot(BA)
        a10 = AC.dot(NBA)
        a11 = BC.dot(NBA)
        b0 = RC.dot(BA)
        b1 = RC.dot(NBA)

        det = a00*a11 - a01*a10

        wa = (a11*b0 - a01*b1)/det
        wb = (-a10*b0 + a00*b1)/det
        wc = 1 - wa - wb

        # calculate the distance with the weighted vectors and subtract that result from our point Q
        D = Q - (wa * A + wb * B + wc * C)

        # add the values
        mhclo_line["weights"] = [wa, wb, wc]
        mhclo_line["offsets"] = [D[0], D[2], -D[1]]
        # TODO: Legacy also multiplies with scales -- [ D[0] * self.scales[0], D[1] * self.scales[1], D[2] * self.scales[2] ]

        _LOG.debug("Legacy mhclo line", mhclo_line)

        self.mhclo_line = mhclo_line

    def _alternative_bake(self, selected_verts):
        # Stub for rewritten bake
        pass

    def _attempt_exact_match(self):
        """In the EXACT strategy, we look for a target vertex which is within 0.001 distance of the focus vertex.
        It this is found, we assume that the intent is that the focus vert and the target vert should share the same space"
        In MHCLO, this vert line will end up only containing a vertex index."""

        _LOG.enter()
        closest = MeshService.closest_vertices(
            self.focus_obj,
            self.focus_vert_index,
            self.target_obj,
            self.target_crossref.vertex_coordinates_kdtree,
            number_of_matches=1)

        if not closest or len(closest) < 1:
            return

        _LOG.debug("EXACT closest", closest[0])

        (vector, index, distance) = closest[0]
        if distance < 0.001:
            self.final_strategy = "EXACT"
            self.exact_match_index = index
            self.exact_match_coord = vector
            _LOG.debug("Exact match", (self.exact_match_index, self.exact_match_coord))

            self.mhclo_line = dict()
            self.mhclo_line["verts"] = [index, index, index]
            self.mhclo_line["weights"] = [1, 0, 0]
            self.mhclo_line["offsets"] = [0, 0, 0]
        else:
            _LOG.debug("Distance is too large for EXACT match", distance)

    def _attempt_simple_face_match(self):
        """In the SIMPLE_FACE strategy, we pick up the face (actually its median point) which is closest to the focus vertex.
        We then make sure that all vertices in the face are part of a vertex group with the same name as the focus vertex group.

        If the distance between the face median point and the focus vertex is less than the shortest distance between the face
        median point and any vertex belonging to the face, we conclude that the focus vert is with almost full certainty within
        the bounds of the face, and that this is the best face to match against.

        If the shortest distance criterion is not met, we check if the angle between the face normal and the vector between the
        face median point and the focus vertex is within an acceptable range (a maximum deviation of 45 degrees).

        If either criterion is met, we pick the three closest vertices in the face to match against.

        In MHCLO, this will end up as a standard three vertex match line."""

        _LOG.enter()
        coord = self.focus_crossref.vertex_coordinates[self.focus_vert_index]
        # TODO: adjust coord for world space locations of focus object vs target object
        closest = self.target_crossref.face_median_points_kdtree.find(coord)

        _LOG.debug("SIMPLE_FACE closest", closest)

        if not closest:
            return

        (vector, index, distance) = closest

        _LOG.debug("Target face index", index)

        target_verts_in_matched_face = self.target_crossref.vertices_by_face[index]
        _LOG.debug("Target verts in matched face", target_verts_in_matched_face)

        for vert_idx in target_verts_in_matched_face:
            if vert_idx not in self.target_crossref.vertices_by_group[self.target_group_idx]:
                # We've found a face which is close to the focus vertex. However, at least one of the vertices in the face
                # is not part of a vertex group with the same name as the focus vertex group.
                _LOG.debug("Vertex group criterion for SIMPLE_FACE not met: vgroup =", self.focus_vert_group_name)
                return

        _LOG.debug("All verts in SIMPLE_FACE belong to an appropriate vertex group")

        # TODO: Do comparison against mean distance

        # TODO: Check angle between face normal and vector between face median point and focus vertex

        self._bake_best_verts_match(target_verts_in_matched_face)
        self.final_strategy = "SIMPLE_FACE"

    def _attempt_extended_face_match(self):
        """In the EXTENDED_FACE strategy, we find the 20 closest faces which belong to the appropriate vertex group. Then we
        go through the faces in order of distance and pick the first one with an acceptable angle between normal and match vector."""

        relevant_face_indices = self.target_crossref.faces_by_group[self.target_group_idx]

        if len(relevant_face_indices) == 0:
            _LOG.debug("Relevant vgroup does not have any faces")
            return

        potential_faces = []
        kd = self.target_crossref.face_median_points_by_group_kdtrees[self.target_group_idx]

        for (coord, index, dist) in kd.find_n(self.focus_vert_coord, 20):
            _LOG.dump("(coord, index, dist)", (coord, index, dist))
            potential_faces.append(index)

        if len(potential_faces) == 0:
            _LOG.debug("No potential faces for EXTENDED_FACE")
            return

        distances = []
        focus_point = self.focus_vert_coord
        for face_idx in potential_faces:
            median_point = self.target_crossref.face_median_points[face_idx]
            distance = self._distance(focus_point, median_point)
            angle = 0.0
            _LOG.dump("(face, focus, median, distance, angle)", (face_idx, focus_point, median_point, distance, angle))
            distances.append({
                "face_idx": face_idx,
                "focus_point": focus_point,
                "median_point": median_point,
                "distance": distance,
                "angle": angle
                })

        sorted_distances = sorted(distances, key=lambda x: x["distance"])
        _LOG.dump("sorted_distances", sorted_distances)

        # First check if closest has an angle less than 30 degrees. In that case, it's good enough.
        for distance in sorted_distances:
            if distance["angle"] < 30.0:
                self.final_strategy = "EXTENDED_FACE"
                _LOG.debug("Closest face also has good angle", distance)
                self._bake_best_verts_match(self.target_crossref.vertices_by_face[distance["face_idx"]])
                return

        # TODO: Continue looking through the list for acceptable fits

