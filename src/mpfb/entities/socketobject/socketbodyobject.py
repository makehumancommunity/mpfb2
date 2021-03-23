
"""This module only contains the SocketProxyObject. See the class docstring
for more info."""

import numpy

from mpfb.services.logservice import LogService
from mpfb.services.socketservice import SocketService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from .socketmeshobject import SocketMeshObject
from mpfb.entities.objectproperties import GeneralObjectProperties
from ._extra_vertex_groups import vertex_group_information

_LOG = LogService.get_logger("socketobject.socketbodyobject")

class SocketBodyObject(SocketMeshObject):
    """This is a helper object for importing the base mesh (ie the base human)
    from MakeHuman. We get the data as numpy arrays from MH, and the idea here is
    to sort and transform things as far as possible in numpy before applying the
    data as a blender mesh object."""

    def __init__(self, importer_presets=None):
        """Construct a SocketBodyObject and populate it with numpy data and other
        info fetched from MH via socket."""

        SocketMeshObject.__init__(self, importer_presets=importer_presets, object_type="Basemesh")
        _LOG.debug("Constructing new socket body object")

        self._object_info = SocketService.get_body_mesh_info()
        _LOG.dump("object_info", self._object_info)
        self.arrange_vertices(SocketService.get_body_vertices())
        self.arrange_faces(SocketService.get_body_faces())
        self.arrange_uv_and_texco(SocketService.get_body_uv_mapping(), SocketService.get_body_texture_coords())
        self.arrange_face_group_arrays()
        if importer_presets["extra_vertex_groups"]:
            self.arrange_extra_vertex_groups()
        self.arrange_face_mask_array(mask_applicable_to_group="body")
        self.arrange_helper_face_group_arrays()
        self._skeleton_info = None

        # If we're able to apply a rig, this will be changed later
        self._has_rig = False

        if "import_rig" in importer_presets and importer_presets["import_rig"]:
            self.arrange_skeleton_info()

        if not self._skeleton_info is None and self._has_rig:
            self._weight_info = SocketService.get_body_weight_info()
            _LOG.dump("weight info", self._weight_info)
            weights_vertices_data = SocketService.get_body_weight_vertices()
            weights_data = SocketService.get_body_weights()
            self.arrange_weights(weights_vertices_data, weights_data)
        else:
            _LOG.debug("No skeleton present, not importing weights")

    def has_rig(self):
        """If there is a defined skeleton that we plan to apply"""
        return self._has_rig

    def get_ground_joint_mean(self):
        """Return the z coordinate for the center of the joint cube representing the ground"""
        _LOG.enter()
        joint = self._vertex_groups_by_name["joint-ground"]
        _LOG.dump("joint", joint)
        joint_verts = self._vertices[joint]
        _LOG.dump("joint_verts", joint_verts)
        z_column = joint_verts[:, 2]
        _LOG.dump("z_column", z_column)
        combined = numpy.sum(z_column) # sum of values in Z column
        average = combined / joint.size
        return average

    def arrange_extra_vertex_groups(self):
        """Take information from the _extra_vertex_groups dict and use it to create extra vertex
        groups on the body."""
        group_info = vertex_group_information["basemesh"]
        self.create_vertex_groups_from_dict(group_info)

    def arrange_helper_face_group_arrays(self):
        """Setup vertex groups for vertices in the helper geometry."""
        _LOG.enter()
        group_names = self._vertex_groups_by_name.keys()
        helper_geometry = []
        joint_cubes = []
        for name in group_names:
            group_array = self._vertex_groups_by_name[name]
            if str(name).startswith("helper-"):
                helper_geometry.append(group_array)
            if str(name).startswith("joint-"):
                joint_cubes.append(group_array)
        self._vertex_groups_by_name["HelperGeometry"] = numpy.concatenate(helper_geometry)
        self._vertex_groups_by_name["JointCubes"] = numpy.concatenate(joint_cubes)

    def arrange_skeleton_info(self):
        """Fetch information about the rig from MH"""
        _LOG.enter()
        self._skeleton_info = SocketService.get_skeleton()
        _LOG.dump("skeleton info", self._skeleton_info)
        self._has_rig = self._skeleton_info["name"] != "none" and len(self._skeleton_info["bones"]) > 0

    def _create_mesh_object(self, mesh_name):
        """Create the actual blender object for the basemesh, and apply vertex groups and modifiers for it"""
        obj = ObjectService.create_blender_object_with_mesh(mesh_name)
        _LOG.debug("obj", obj)
        mesh = obj.data
        _LOG.debug("mesh", mesh)

        _LOG.debug("Verts length", len(self._vertices))
        _LOG.debug("Faces length", len(self._faces))

        del_helpers = self._importer_presets["handle_helpers"] == "DELETE"

        vertices_to_add = self._vertices
        faces_to_add = self._faces

        if del_helpers:
            # Helper geometry should be removed rather than simply masked.
            # TODO: this entire section is buggy and should be reviewd
            last_body_vertex = numpy.max(self._vertex_groups_by_name["body"]) + 1
            _LOG.debug("last_body", last_body_vertex)
            vertices_to_add = self._vertices[0:last_body_vertex, :]
            _LOG.dump("verts", vertices_to_add)

            last_body_face = 0
            for face_group in self._object_info["faceGroups"]:
                if face_group["name"] == "body":
                    start_stop = face_group["fgStartStops"][0]
                    last_body_face = start_stop[1]

            faces_to_add = self._faces[0:last_body_face, :]

        # Next most efficient available way to convert a set of numpy arrays to a mesh.
        # The most efficient way listed online causes segfaults for me and is hard to
        # understand.
        mesh.from_pydata(vertices_to_add.tolist(), [], faces_to_add.tolist())

        for polygon in mesh.polygons:
            polygon.use_smooth = True

        # Create all relevant vertex groups
        for name in self._vertex_groups_by_name:
            exclude = False
            if del_helpers:
                # Do not create vertex groups for anything but the body if we're
                # going to exclude the helpers anyway
                exclude = name != "body"
            if not self._importer_presets["detailed_helpers"]:
                # Only created detailed helper groups ("hair", "skirt"...) if requested
                exclude = str(name).startswith("helper-") or str(name).startswith("joint-")
            if not exclude:
                # Add all vertices to a new group, with a weight of 1.0
                vgroup = obj.vertex_groups.new(name=name)
                vgroup.add(self._vertex_groups_by_name[name].tolist(), 1.0, 'ADD')

                # Update weights with actual weight values
                self.apply_vertex_weights_if_needed(mesh, vgroup)
            else:
                _LOG.debug("Not creating vertex group", name)

        self.create_uv_layer(obj.data)

        if self._importer_presets["handle_helpers"] == "MASK":
            modifier = obj.modifiers.new("Hide helpers", 'MASK')
            modifier.vertex_group = "body"
            modifier.show_in_editmode = True
            modifier.show_on_cage = True

        if self._importer_presets["add_subdiv_modifier"]:
            modifier = obj.modifiers.new("Subdivision", 'SUBSURF')
            modifier.levels = 0
            modifier.render_levels = self._importer_presets["subdiv_levels"]

        if "Delete" in self._vertex_groups_by_name and self._vertex_groups_by_name["Delete"].size > 0:
            mask = obj.modifiers.new("Hide delete group", 'MASK')
            mask.vertex_group = "Delete"
            mask.show_in_editmode = True
            mask.show_on_cage = True
            mask.invert_vertex_group = True

        return obj

    def as_blender_mesh_object(self, collection=None):
        """Use all the collected numpy data and transform to construct a blender mesh object. This will
        also create and apply a rig if available and requested."""
        _LOG.enter()

        import_rig = self._importer_presets["import_rig"]
        import_body = self._importer_presets["import_body"]

        name = self._object_info.get("name", "Human")

        obj = None
        parent = None

        mesh_name = name

        if import_rig and self.has_rig() and self._importer_presets["prefix_object_names"]:
            mesh_name = name + ".body"

        if import_rig and self.has_rig() and not self._importer_presets["prefix_object_names"]:
            mesh_name = "body"

        if import_body:
            obj = self._create_mesh_object(mesh_name)
            # Custom properties identifying the mesh
            GeneralObjectProperties.set_value("object_type", "Basemesh", obj)
            GeneralObjectProperties.set_value("scale_factor", self._scale, obj)

        if import_rig and self.has_rig():
            # If a rig is available, we'll likely want to use it as parent for the mesh
            parent = RigService.create_rig_from_skeleton_info(name, self._skeleton_info, parent=None, scale=self._scale)
            # Custom property identifying the rig
            GeneralObjectProperties.set_value("object_type", "Skeleton", parent)

        if obj:
            obj_parent = None
            if self._importer_presets["rig_as_parent"]:
                obj_parent = parent
            ObjectService.link_blender_object(obj, collection=collection, parent=obj_parent)

        if parent and obj:
            if parent.type == "ARMATURE":
                modifier = obj.modifiers.new("Armature", 'ARMATURE')
                modifier.object = parent

        return (obj, parent)

