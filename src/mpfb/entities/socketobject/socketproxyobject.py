"""This module only contains the SocketProxyObject. See the class docstring
for more info."""

import numpy, bpy
from ...services import LogService
from ...services import SocketService
from ...services import ObjectService
from ...services import ModifierService
from .socketmeshobject import SocketMeshObject
from mpfb.entities.objectproperties import GeneralObjectProperties
from ._extra_vertex_groups import vertex_group_information

_LOG = LogService.get_logger("socketobject.socketbodyobject")

class SocketProxyObject(SocketMeshObject):
    """This is a helper object for importing proxies (bodyproxies, clothes...)
    from MakeHuman. We get the data as numpy arrays from MH, and the idea here is
    to sort and transform things as far as possible in numpy before applying the
    data as a blender mesh object."""

    def __init__(self, proxy_info, importer_presets=None, import_weights=False):
        """Construct a SocketProxyObject and populate it with numpy data and other
        info fetched from MH via socket."""

        SocketMeshObject.__init__(self, importer_presets=importer_presets, object_type=proxy_info["type"])
        _LOG.debug("Constructing new socket proxy object of type", proxy_info["type"])

        self._object_info = dict(proxy_info)
        self._has_rig = import_weights

        # The socket plugin does not expose the following values for proxies, or at least not
        # always. This is probably a bug that should be fixed in the socket service, but we
        # will provide sensible defaults as a workaround here

        if "verticesShape" not in self._object_info:
            num_vertices = self._object_info["numVertices"]
            self._object_info["verticesShape"] = [num_vertices, 3]

        if "facesShape" not in self._object_info:
            num_faces = self._object_info["numFaces"]
            self._object_info["facesShape"] = [num_faces, 4]

        if "textureCoordsShape" not in self._object_info:
            num_texture_coords = self._object_info["numTextureCoords"]
            self._object_info["textureCoordsShape"] = [num_texture_coords, 2]

        if "faceUVMappingsShape" not in self._object_info:
            num_uv = self._object_info["numFaceUVMappings"]
            self._object_info["faceUVMappingsShape"] = [num_uv, 4]

        _LOG.dump("object_info", self._object_info)

        uuid = self._object_info["uuid"]

        self.arrange_vertices(SocketService.get_proxy_vertices(uuid))
        self.arrange_faces(SocketService.get_proxy_faces(uuid))
        self.arrange_uv_and_texco(SocketService.get_proxy_uv_mapping(uuid), SocketService.get_proxy_texture_coords(uuid))
        self.arrange_face_group_arrays()
        self.arrange_face_mask_array()
        self.arrange_extra_vertex_groups()

        if import_weights:
            _LOG.debug("Will later attempt to weight proxy", self._object_info["name"])
            self._weight_info = SocketService.get_proxy_weight_info(uuid)
            _LOG.dump("weight info", self._weight_info)
            weights_vertices_data = SocketService.get_proxy_weight_vertices(uuid)
            weights_data = SocketService.get_proxy_weights(uuid)
            self.arrange_weights(weights_vertices_data, weights_data)
        else:
            _LOG.debug("Will not attempt to weight proxy", self._object_info["name"])

    def get_lowest_point(self):
        """Find the vertex coordinate with the lowest Z value"""
        _LOG.enter()
        return numpy.amin(self._vertices[:, 2]) # minimum value in Z column

    def arrange_extra_vertex_groups(self):
        """Take information from the _extra_vertex_groups dict and use it to create extra vertex
        groups on the body."""
        if not "uuid" in self._object_info:
            return
        uuid = self._object_info["uuid"]
        if uuid in vertex_group_information:
            group_info = vertex_group_information[uuid]
            self.create_vertex_groups_from_dict(group_info)

    def as_blender_mesh_object(self, parent=None, name_prefix=None):
        """Use all the collected numpy data and transform to construct a blender mesh object"""
        _LOG.enter()

        name = self._object_info.get("name", '')

        if name_prefix:
            name = name_prefix.split(".")[0] + "." + name  # check if prefix has a trailing dot

        obj = ObjectService.create_blender_object_with_mesh(name, skip_linking=True)

        # Set custom properties for the generated blender object
        GeneralObjectProperties.set_value("object_type", self._object_info["type"], obj)
        GeneralObjectProperties.set_value("scale_factor", self._scale, obj)

        mesh = obj.data

        # Next most efficient available way to convert a set of numpy arrays to a mesh.
        # The most efficient way listed online causes segfaults for me and is hard to
        # understand.
        mesh.from_pydata(self._vertices.tolist(), [], self._faces.tolist())

        _LOG.dump("Vertex groups", self._vertex_groups_by_name)

        for polygon in mesh.polygons:
            # Assume all faces are smooth. At least we have no way of representing
            # sharp faces in MH
            polygon.use_smooth = True

        for name in self._vertex_groups_by_name:
            # Add all vertices to a group, with a vertex weight of 1.0.
            vgroup = obj.vertex_groups.new(name=name)
            vgroup.add(self._vertex_groups_by_name[name].tolist(), 1.0, 'ADD')

            # Update vertex weights with actual weights
            self.apply_vertex_weights_if_needed(mesh, vgroup)

        self.create_uv_layer(obj.data)

        if self._importer_presets["add_subdiv_modifier"]:
            modifier = obj.modifiers.new("Subdivision", 'SUBSURF')
            modifier.levels = 0 # viewport level
            modifier.render_levels = self._importer_presets["subdiv_levels"]

        _LOG.debug("parent", parent)
        if parent and parent.type == "ARMATURE":
            ModifierService.create_armature_modifier(obj, parent, "Armature")

        if "Delete" in self._vertex_groups_by_name and self._vertex_groups_by_name["Delete"].size > 0:
            mask = obj.modifiers.new("Hide delete group", 'MASK')
            mask.vertex_group = "Delete"
            mask.show_in_editmode = True
            mask.show_on_cage = True
            mask.invert_vertex_group = True

        ObjectService.link_blender_object(obj, collection=None, parent=parent)
        return obj

