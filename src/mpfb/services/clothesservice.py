"""This module contains utility functions for clothes."""

import random
from mathutils import Vector
from mpfb.services.objectservice import ObjectService
from mpfb.services.logservice import LogService
from mpfb.entities.objectproperties import GeneralObjectProperties

_LOG = LogService.get_logger("services.clothesservice")
_LOG.set_level(LogService.DEBUG)

class ClothesService:
    """Utility functions for clothes."""

    def __init__(self):
        """You should not instance ClothesService. Use its static methods instead."""
        raise RuntimeError("You should not instance ClothesService. Use its static methods instead.")

    @staticmethod
    def fit_clothes_to_human(clothes, basemesh, mhclo=None):
        """Move clothes vertices so they fit the current shape of the base mesh."""

        if basemesh is None:
            raise ValueError('Cannot refit to None basemesh')

        if clothes is None:
            raise ValueError('Cannot refit to None clothes')

        if not ObjectService.object_is_basemesh(basemesh):
            raise ValueError('The provided object is not a basemesh')

        if mhclo is None:
            raise NotImplemented("Searching for MHCLO info is not implemented yet, you must provide the MHCLO object")

        # We cannot rely on the vertex position data directly, since it represent positions
        # as they are *before* targets are applied. We want the shape of the mesh *after*
        # targets are applied.
        #
        # We will therefore create a new shape key "from mix". This means it will have the
        # combined state of all current shape keys. Then we will use that shape key for
        # getting vertex positions.
        key_name = "temporary_fitting_key." + str(random.randrange(1000, 9999))
        basemesh.shape_key_add(name=key_name, from_mix=True)
        shape_key = basemesh.data.shape_keys.key_blocks[key_name]
        human_vertices = shape_key.data
        human_vertices_count = len(human_vertices)

        scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=basemesh)
        if not scale_factor:
            scale_factor = 1.0

        # Fallback for if no scale is specified in mhclo
        z_size = y_size = x_size = scale_factor

        if mhclo.x_scale:
            if mhclo.x_scale[0] >= human_vertices_count or mhclo.x_scale[1] > human_vertices_count \
                or mhclo.y_scale[0] >= human_vertices_count or mhclo.y_scale[1] >= human_vertices_count \
                or mhclo.z_scale[0] >= human_vertices_count or mhclo.z_scale[1] >= human_vertices_count:
                _LOG.warn("Giving up refitting, not inside")
                raise ValueError("Cannot refit as we are not inside")

            x_size = abs(human_vertices[mhclo.x_scale[0]].co[0] - human_vertices[mhclo.x_scale[1]].co[0]) / mhclo.x_scale[2]
            y_size = abs(human_vertices[mhclo.y_scale[0]].co[2] - human_vertices[mhclo.y_scale[1]].co[2]) / mhclo.y_scale[2]
            z_size = abs(human_vertices[mhclo.z_scale[0]].co[1] - human_vertices[mhclo.z_scale[1]].co[1]) / mhclo.z_scale[2]

        _LOG.debug("x_scale, y_scale, z_scale", (mhclo.x_scale, mhclo.y_scale, mhclo.z_scale))
        _LOG.debug("x_size, y_size, z_size", (x_size, y_size, z_size))

        clothes_vertices = mhclo.clothes.data.vertices

        _LOG.debug("About to try to match vertices: ", len(clothes_vertices))
        _LOG.dump("Verts", mhclo.verts)

        for clothes_vertex_number in range(len(clothes_vertices)):
            vertex_match_info = mhclo.verts[clothes_vertex_number]
            (human_vertex1, human_vertex2, human_vertex3) = vertex_match_info["verts"]

            # test if we inside mesh, if not, no chance
            #
            if human_vertex1 >= human_vertices_count or human_vertex2 > human_vertices_count or human_vertex3 >= human_vertices_count:
                continue

            offset = [vertex_match_info["offsets"][0]*x_size, vertex_match_info["offsets"][1]*z_size, vertex_match_info["offsets"][2]*y_size]
            clothes_vertices[clothes_vertex_number].co = \
                vertex_match_info["weights"][0] * human_vertices[human_vertex1].co + \
                vertex_match_info["weights"][1] * human_vertices[human_vertex2].co + \
                vertex_match_info["weights"][2] * human_vertices[human_vertex3].co + \
                Vector(offset)

        # We need to take into account that the base mesh might be rigged. If it is, we'll want the rig position
        # rather than the basemesh position
        if basemesh.parent:
            clothes.location = (0.0, 0.0, 0.0)
            clothes.parent = basemesh.parent
        else:
            clothes.location = basemesh.location

        # As we are finished with the combined shape key we can now remove it
        basemesh.shape_key_remove(shape_key)

    @staticmethod
    def update_delete_group(mhclo, basemesh, replace_delete_group=False, delete_group_name=None, add_modifier=True, skip_if_empty_delete_group=True):
        """Create or update a "delete" group on the base mesh."""

        if skip_if_empty_delete_group:
            if not mhclo.delete or not mhclo.delverts or len(mhclo.delverts) < 1:
                # mhclo has empty delete group. There's no point continuing.
                return

        if delete_group_name is None:
            if mhclo.delete_group is None:
                delete_group_name = "Delete"
            else:
                delete_group_name = mhclo.delete_group

        # If requested, remove the previously existing delete group.
        if replace_delete_group and mhclo.delete and delete_group_name in basemesh.vertex_groups:
            vertex_group = basemesh.vertex_groups.get(delete_group_name)
            basemesh.vertex_groups.remove(vertex_group)

        # We'll want to set up the delete group even if it doesn't contain any vertices. This
        # so that a modifier won't fail later on
        if delete_group_name not in basemesh.vertex_groups:
            delete_group = basemesh.vertex_groups.new(name=delete_group_name)
        else:
            delete_group = basemesh.vertex_groups.get(delete_group_name)

        human_vertices_count = len(basemesh.data.vertices)

        # If the clothes do not have a defined delete group, we can skip the next step
        if mhclo.delete:
            # Find vertices to delete. For safety check so that the vertex index actually
            # exist in the base mesh. It might refer to a helper index that have been excluded
            # or deleted.
            delete_vertices_list = []
            for vertex_to_delete in  mhclo.delverts:
                if vertex_to_delete < human_vertices_count:
                    delete_vertices_list.append(vertex_to_delete)

            # Add the delete vertices to the previously created vertex group
            delete_group.add(delete_vertices_list, 1.0, 'ADD')

        has_applicable_modifier = False

        for modifier in basemesh.modifiers:
            if modifier.type == "MASK":
                if modifier.vertex_group == delete_group_name:
                    has_applicable_modifier = True

        if add_modifier and not has_applicable_modifier:
            modifier = basemesh.modifiers.new(name=delete_group_name, type="MASK")
            modifier.vertex_group = delete_group_name
            modifier.invert_vertex_group = True

    @staticmethod
    def interpolate_weights(basemesh, clothes, rig, mhclo):
        """Try to copy rigging weights from the base mesh to the clothes mesh, hopefully
        making the clothes fit the provided rig."""

        # Create an empty outline with placeholders arrays that will contain lists of
        # vertices + weights per vertex group
        clothes_weights = dict()
        for bone in rig.data.bones:
            # The vertex groups have the same names as the bones
            clothes_weights[str(bone.name)] = []

        # Build cross reference dicts to easily map between a vertex group index and
        # a vertex group name
        group_name_to_index = dict()
        group_index_to_name = dict()
        for group in basemesh.vertex_groups:
            if str(group.name) in clothes_weights:
                group_name_to_index[str(group.name)] = group.index
                group_index_to_name[int(group.index)] = str(group.name)

        # We will now iterate over the vertices in the clothes. The idea is to then
        # look up the vertices on the human that the clothes vertex is tied to. This
        # information is provided in the mhclo object.
        #
        # For each mapping of clothes vertex to human vertex we also have a weight,
        # so that clothes vertex 1 might be 20% tied to human vertex 1 and 40% tied to
        # human vertex 2 and so on.
        #
        # By multiplying that weight with the vertex group weight of the human vertex, we
        # get the interpolated vertex group weight for the clothes vertex.
        for vert_number in range(len(mhclo.verts)):
            clothes_vert = mhclo.verts[vert_number]
            groups = dict()
            for match_vert in range(3):
                # Which human vert is the clothes vert tied to?
                human_vert = basemesh.data.vertices[clothes_vert["verts"][match_vert]]

                # .. and by how much?
                assigned_weight = clothes_vert["weights"][match_vert]

                # Iterate over all vertex groups the human vert belongs to
                for group in human_vert.groups:
                    idx = group.group
                    if idx in group_index_to_name:
                        if not idx in groups:
                            groups[idx] = []
                        # Add the calculated weight to the list of found weights
                        #
                        # Human vertex group weight * Human vertex weight
                        groups[idx].append(group.weight * assigned_weight)

            # Iterate over all found vertex groups for the current clothes vertex
            # and calculcate the average weight for each group
            for idx in groups.keys():
                average_weight = sum(groups[idx]) / len(groups[idx])
                # If the caculated average weight is below 0.001 we will ignore it. This
                # makes the interpolation much faster later on
                if average_weight > 0.001:
                    group_name = group_index_to_name[int(idx)]
                    clothes_weights[group_name].append([vert_number, average_weight])

        # We now have a finished map with all weights. We will iterate over this
        # and convert each weight array to a vertex group on the clothes, and then
        # set the vertex weights in it
        for group_name in clothes_weights.keys():
            # Weights is an array looking like [ [vert_index, weight], [vert_index, weight]...]
            weights = clothes_weights[group_name]

            # No need to create a vertex group if no weights were found for it. For example,
            # it is unnecessary to have an "upperarm02" group for shoes.
            if len(weights) > 0:
                # We want the vertex indices as a list. By using zip we can rotate the array
                # so that columns become rows
                rotated = zip(*weights)

                # We can now get the indices from the first column
                indices = list(rotated)[0]

                # Create a vertex group and add all vertices to it, with a weight of 1.0.
                # It is much faster to to it like this and then update the weights than
                # adding the vertices one by one with its weight
                new_vert_group = clothes.vertex_groups.new(name=str(group_name))
                new_vert_group.add(indices, 1.0, 'ADD')
                group_index = new_vert_group.index

                # Iterate over the weights and update the vertex weights in the group
                for weight_info in weights:
                    vertex_index = weight_info[0]
                    weight = weight_info[1]
                    for group in clothes.data.vertices[vertex_index].groups:
                        if int(group.group) == group_index:
                            group.weight = weight


    @staticmethod
    def set_makeclothes_object_properties_from_mhclo(clothes_object, mhclo, delete_group_name=None):
        """This will update the clothes object's properties with metadata values
        from the mhclo object."""

        from mpfb.ui.makeclothes import MakeClothesObjectProperties

        properties = [
            "author",
            "delete_group",
            "description",
            "homepage",
            "license",
            "name",
            "tag",
            "z_depth"
            ]

        for property_name in properties:
            if hasattr(mhclo, property_name):
                value = getattr(mhclo, property_name)
                if not value is None:
                    MakeClothesObjectProperties.set_value(property_name, value, entity_reference=clothes_object)

        if not delete_group_name is None:
            MakeClothesObjectProperties.set_value("delete_group", delete_group_name, entity_reference=clothes_object)
