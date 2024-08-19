
"""This module only contains the SocketMeshObject. See the class docstring
for more info."""

import gc, numpy
from ...services import LogService

_LOG = LogService.get_logger("socketobject.socketmeshobject")

class SocketMeshObject:
    """This is an abstract helper object for importing meshes from MakeHuman.
    We get the data as numpy arrays from MH, and the idea here is to sort
    and transform things as far as possible in numpy before applying the
    data as a blender mesh object."""

    def __init__(self, importer_presets=None, object_type="GENERAL"):
        """Construct a SockeMeshObject. Normally this is only called by
        descendants. It is unlikely you want to directly instance a
        SocketMeshObject."""

        # TODO: Make sure importer_presets is a dict, not a sceneconfigset

        _LOG.debug("Constructing new socket mesh object")
        self._importer_presets = importer_presets
        self._object_info = dict()
        self._object_type = object_type
        self._vertices = None
        self._faces = None
        self._texco = None
        self._uvmappings = None
        self._sorted_face_uv_and_texco = None
        self._vertex_groups_by_name = dict()
        self._vertex_groups_by_index = dict()
        self._weight_info = dict()
        self._weights_by_name = dict()
        self._scale = 1

    def __del__(self):
        """Function aimed at trying to help garbage collection along a bit.
        It is not immediately obvious it does much difference, but it
        probably doesn't hurt either"""

        _LOG.enter()
        _LOG.debug("This socket mesh object is about to be destroyed. Trying to help GC along a bit by destroying large structures.")
        del self._vertices
        del self._faces
        del self._vertex_groups_by_index
        del self._vertex_groups_by_name
        gc.collect()

    def get_importer_presets(self):
        """Getter for the importer presets, which is a dict that should have been given in the constructor"""
        _LOG.enter()
        return self._importer_presets

    def get_object_info(self):
        """Getter for object information: That is, the initial information about the object,
        fetched from MakeHuman via the socket."""
        _LOG.enter()
        return self._object_info

    def get_object_type(self):
        """Getter for object type. Type is Basemesh, Proxymeshes, Clothes, Eyes and so on and so forth."""
        _LOG.enter()
        return self._object_type

    def get_name(self):
        """Convenience call from getting name from object_info"""
        _LOG.enter()
        return self._object_info["name"]

    def get_filename(self):
        """Convenience call from getting filename from object_info"""
        _LOG.enter()
        return  self._object_info["filename"]

    def convert_to_shaped_numpy_array(self, shape_key, type_code_key, data_from_socket, rescale=None):
        """Convenience method for converting any byte array to a numpy array with the proper shape.
        shape_key and type_code_key are which keys in the object info that contains the information
        about the shape and type respective. The data_from_socket param is expected to be raw binary
        output from SocketService. Rescale is a multiplication value that is applied to all individual
        values in the resulting array."""
        _LOG.enter()
        shape = self._object_info[shape_key]
        type_code = self._object_info[type_code_key]
        _LOG.debug("shape to attempt to convert to", shape)
        _LOG.debug("type code to attempt to convert to", type_code)
        numpy_raw_data = numpy.frombuffer(data_from_socket, type_code)
        _LOG.dump("numpy_raw_data", numpy_raw_data)
        scaled_data = numpy_raw_data
        if not rescale is None:
            scaled_data = numpy_raw_data * rescale
        _LOG.dump("scaled_data", scaled_data)
        reshaped_data = scaled_data.reshape(shape)
        _LOG.dump("reshaped_data", reshaped_data)
        return reshaped_data

    def arrange_vertices(self, data_from_socket):
        """Take a raw byte array, expected to represent a numpy array as fetched via the SocketService,
        and convert it to a multidimensional array containing info about vertex positions."""
        _LOG.enter()

        scale = None
        scale_factor_name = self._importer_presets["scale_factor"]
        if scale_factor_name == "DECIMETER":
            _LOG.debug("Not scaling vertices")
        if scale_factor_name == "METER":
            _LOG.debug("Scaling vertices with 0.1")
            scale = 0.1
            self._scale = scale
        if scale_factor_name == "CENTIMETER":
            _LOG.debug("Scaling vertices with 10.0")
            scale = 10.0
            self._scale = scale

        self._vertices = self.convert_to_shaped_numpy_array("verticesShape", "verticesTypeCode", data_from_socket, scale)

        # MakeHuman sends verts in XZY order, so switch places of Z and Y. Yeah, the syntax is crazy, but basically
        # it just swaps the positions of columns in a twodimensional array.
        self._vertices[:, [1, 2]] = self._vertices[:, [2, 1]]

        # Further, MakeHuman's Y is -Y in blender, so multiply Y with -1
        self._vertices[:, 1] *= -1

        _LOG.dump("final reshaped vertices", self._vertices)

    def arrange_faces(self, data_from_socket):
        """Take a raw byte array, expected to represent a numpy array as fetched via the SocketService,
        and convert it to a multidimensional array containing info about faces."""
        _LOG.enter()
        self._faces = self.convert_to_shaped_numpy_array("facesShape", "facesTypeCode", data_from_socket)

    def arrange_uv_and_texco(self, uv_data_from_socket, texco_data_from_socket):
        """Take two raw byte arrays, expected to represent numpy arrays as fetched via the SocketService,
        and convert them to information about texture coordinates and UV mappings."""
        _LOG.enter()
        self._texco = self.convert_to_shaped_numpy_array("textureCoordsShape", "textureCoordsTypeCode", texco_data_from_socket)
        self._uvmappings = self.convert_to_shaped_numpy_array("faceUVMappingsShape", "faceUVMappingsTypeCode", uv_data_from_socket)

        # Yet another crazy syntax. But this line combines the texco and uvmappings arrays into one by using the uv mappings
        # as indexes for picking values from the texco array
        self._sorted_face_uv_and_texco = self._texco[self._uvmappings[:]]

        _LOG.dump("Sorted uv and texco", self._sorted_face_uv_and_texco)

    def arrange_weights(self, weights_vertices_data, weights_data):
        """Take two raw byte arrays, expected to represent one-dimensional numpy arrays as fetched via the SocketService,
        and convert them to arrays with vertex weights. Before doing this, an implementing subclass must have fetched
        and set _weight_info.
        As a side-effect, the vertex groups will be calculated for each bone mentioned in _weight_info."""
        _LOG.enter()
        if self._weight_info is None or len(self._weight_info.keys()) < 1:
            raise ValueError("It seems _weight_info was not set by sub class")
        raw_weights_vertices = numpy.frombuffer(weights_vertices_data, numpy.int32)
        raw_weights = numpy.frombuffer(weights_data, numpy.float32)
        _LOG.dump("raw_weights_vertices", raw_weights_vertices)
        _LOG.dump("raw_weights", raw_weights)

        current_position = 0
        for weight_info in self._weight_info["weights"]:
            bone = weight_info["bone"]
            length = weight_info["numVertices"]

            # The goal with the following two operations is to get two parallel arrays where the first array
            # (the vertex group) is a list of vertex indices, and the second array (the weight value)
            # contain vertex weights. This is later used to iterate over each vertex in a vertex group and
            # setting its weight for that group.

            # Add the vertices (as represented by index) to a vertex group with the same name as the bone
            self._vertex_groups_by_name[bone] = raw_weights_vertices[current_position:current_position+length]

            # Pick weights values for the individual vertices and add them to a separate array named as the bone
            self._weights_by_name[bone] = raw_weights[current_position:current_position+length]

            current_position = current_position + length
            #_LOG.dump(bone, weights)

    def arrange_face_group_arrays(self):
        """The information we get from MakeHuman is about *face* groups, not *vertex* groups. This method
        converts the face group information to vertex group information."""
        _LOG.enter()

        if "faceGroups" not in self._object_info:
            _LOG.debug("This object has no face groups")
            return

        for face_group in self._object_info["faceGroups"]:
            name = face_group["name"]
            _LOG.dump("face_group", face_group)
            for start_stop in face_group["fgStartStops"]:
                # A face group is a set of start/stop indexes, such as [ [0, 2], [5, 8] ]
                # representing the faces numbered 0 1 2 5 6 7 8
                start = start_stop[0]
                stop = start_stop[1]

                # _faces contains vertex indexes making up faces. We pick all the faces between
                # start and stop (across all columns) and add it to a new array
                faces = self._faces[start:stop, :]

                # Convert this to a one-dimensional array of vertex indexes
                verts_to_add = numpy.unique(faces.flatten())

                # Add these vertices to the relevant vertex group
                if not name in self._vertex_groups_by_name:
                    self._vertex_groups_by_name[name] = verts_to_add
                else:
                    numpy.concatenate((self._vertex_groups_by_name[name], verts_to_add))

    def create_vertex_groups_from_dict(self, group_information):
        """Take arrays of vertex indices and use these to create extra vertex groups."""
        for name in group_information.keys():
            self._vertex_groups_by_name[name] = numpy.array(group_information[name])

    def arrange_face_mask_array(self, mask_applicable_to_group=None):
        """The face mask is basically the inverted sum total of all combined delete groups.
        This method convert the information about the mask (as defined by a list of *faces*
        to *display*) and converts it to a vertex group to be used as inverted mask (as
        defined as a list of *vertices* to *hide*)"""
        _LOG.enter()

        if "faceMask" not in self._object_info:
            _LOG.debug("This object has no face mask")
            return
        if len(self._object_info["faceMask"]) < 1:
            _LOG.debug("This object has a zero length face mask")
            return

        _LOG.debug("faceMask", self._object_info["faceMask"])

        face_mask_verts = None
        for start_stop in self._object_info["faceMask"]:
            # A face mask is a set of start/stop indexes, such as [ [0, 2], [5, 8] ]
            # representing the faces numbered 0 1 2 5 6 7 8
            _LOG.dump("start_stop", start_stop)
            start = start_stop[0]
            stop = start_stop[1]

            # _faces contains vertex indexes making up faces. We pick all the faces between
            # start and stop (across all columns) and add it to a new array
            faces = self._faces[start:stop, :]

            _LOG.dump("faces", faces)

            # Convert this to a one-dimensional array of vertex indexes
            verts_to_add = numpy.unique(faces.flatten())
            _LOG.dump("verts_to_add", verts_to_add)

            # Add these vertices to the relevant vertex group
            if face_mask_verts is None:
                face_mask_verts = verts_to_add
            else:
                face_mask_verts = numpy.concatenate((face_mask_verts, verts_to_add))

        _LOG.dump("face_mask_verts", face_mask_verts)

        # In case we have given a specific vertex group which should be affected by the
        # face mask, only use vertices which are in the vertex group for calculating
        # which vertices are relevant for the mask. If no group has been specified,
        # all vertices is considered potential candidates
        if mask_applicable_to_group:
            all_verts = self._vertex_groups_by_name[mask_applicable_to_group]
        else:
            all_verts = numpy.arange(0, self._vertices.size, dtype=numpy.int32)

        # Create an inverted mask by finding all vertices *not* listed in the arrays constructed
        # above, and make sure we only mention each vertex once.
        verts_to_hide = numpy.unique(numpy.setdiff1d(all_verts, face_mask_verts, assume_unique=True))

        # The end result is a new vertex group "Delete"
        self._vertex_groups_by_name["Delete"] = verts_to_hide


    def apply_vertex_weights_if_needed(self, mesh, vertex_group):
        """Perform the actual weighting for a particular (blender) vertex group in the specified mesh."""
        _LOG.enter()
        name = vertex_group.name
        if name not in self._vertex_groups_by_name:
            _LOG.warn("Tried to apply vertex weights for a non-existing group:", name)
            return
        if name not in self._weights_by_name:
            _LOG.debug("No weights for group:", name)
            return

        # Here we expect that the vertex group already exist with the proper vertices
        # already added, although with 1.0 as weight for all vertices. We will iterate
        # over the two parallel arrays constructed in arrange_weights() and pick the
        # vertex index from one and the weight from the other
        # Having pre-added all vertices in one operation and then updating the weights
        # is a lot faster than adding each vertex individually together with its weight.
        for vertex_index, vertex_weight in zip(self._vertex_groups_by_name[name], self._weights_by_name[name]):
            vertex = mesh.vertices[vertex_index]
            for group in vertex.groups:
                if group.group == vertex_group.index:
                    group.weight = vertex_weight

    def create_uv_layer(self, mesh):
        """Create a new UV layer for the mesh, based on the uv and texco information
        previously collected"""
        _LOG.enter()
        uv_layer = mesh.uv_layers.new()

        flattened_sorted_uv_texco = self._sorted_face_uv_and_texco.flatten()

        # Crazy blender syntax. Basically we iterate over each point in the uv layer and
        # set its "uv" property to a value in the given array. The first point with pick
        # the first value in the array, the second point the second value and so on
        uv_layer.data.foreach_set("uv", flattened_sorted_uv_texco)

