"""This module contains utility functions for clothes."""

import random, os, bpy, time, bmesh

from mathutils import Vector

from mpfb.entities.rig import Rig
from mpfb.entities.clothes.vertexmatch import VertexMatch
from mpfb.services.objectservice import ObjectService
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.assetservice import AssetService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.clothes.mhclo import Mhclo
from mpfb.entities.meshcrossref import MeshCrossRef
from mpfb.services.rigservice import RigService

_LOG = LogService.get_logger("services.clothesservice")

CLOTHES_REFERENCE_SCALE = {
                        "Body": {
                            "xmin": 13868,
                            "xmax": 14308,
                            "ymin": 10854,
                            "ymax": 10981,
                            "zmin": 881,
                            "zmax": 13137
                        },
                        "Head": {
                            "xmin": 5399,
                            "xmax": 11998,
                            "ymin": 962,
                            "ymax": 5320,
                            "zmin": 791,
                            "zmax": 881
                        },
                        "Teeth": {
                            "xmin": 15077,
                            "xmax": 15111,
                            "ymin": 15061,
                            "ymax": 15068,
                            "zmin": 14993,
                            "zmax": 15061
                        },
                        "Torso": {
                            "xmin": 3924,
                            "xmax": 10589,
                            "ymin": 1892,
                            "ymax": 3946,
                            "zmin": 1524,
                            "zmax": 4370
                        },
                        "Arm": {
                            "xmin": 8300,
                            "xmax": 10210,
                            "ymin": 10076,
                            "ymax": 10543,
                            "zmin": 10064,
                            "zmax": 10069
                        },
                        "Hand": {
                            "xmin": 8938,
                            "xmax": 10548,
                            "ymin": 9864,
                            "ymax": 10267,
                            "zmin": 9881,
                            "zmax": 10318
                        },
                        "Leg": {
                            "xmin": 11133,
                            "xmax": 11141,
                            "ymin": 11130,
                            "ymax": 11135,
                            "zmin": 11025,
                            "zmax": 11460
                        },
                        "Foot": {
                            "xmin": 12839,
                            "xmax": 12860,
                            "ymin": 11609,
                            "ymax": 12442,
                            "zmin": 12828,
                            "zmax": 12888
                        },
                        "Eye": {
                            "xmin": 14618,
                            "xmax": 14645,
                            "ymin": 14650,
                            "ymax": 14658,
                            "zmin": 14636,
                            "zmax": 14663
                        },
                        "Genital": {
                            "xmin": 6335,
                            "xmax": 12932,
                            "ymin": 4347,
                            "ymax": 4376,
                            "zmin": 4335,
                            "zmax": 6431
                        }
                    }

class ClothesService:
    """Utility functions for clothes."""

    def __init__(self):
        """You should not instance ClothesService. Use its static methods instead."""
        raise RuntimeError("You should not instance ClothesService. Use its static methods instead.")

    @staticmethod
    def fit_clothes_to_human(clothes, basemesh, mhclo=None, set_parent=True):
        """Move clothes vertices so they fit the current shape of the base mesh."""

        _LOG.dump("Given MHCLO object", mhclo)

        if basemesh is None:
            raise ValueError('Cannot refit to None basemesh')

        if clothes is None:
            raise ValueError('Cannot refit to None clothes')

        if not ObjectService.object_is_basemesh(basemesh):
            raise ValueError('The provided object is not a basemesh')

        if mhclo is None:
            mhclo_fragment = GeneralObjectProperties.get_value("asset_source", entity_reference=clothes)
            object_type = ObjectService.get_object_type(clothes)

            if mhclo_fragment and object_type:
                mhclo_path = AssetService.find_asset_absolute_path(mhclo_fragment, str(object_type).lower())
                if not mhclo_path:
                    raise IOError(mhclo_fragment + " does not exist")
                if not os.path.exists(mhclo_path):
                    raise IOError(mhclo_path + " does not exist")
                mhclo = Mhclo()
                mhclo.load(mhclo_path)
            else:
                raise ValueError('There is not enough info to refit this asset, at least asset source and object type is needed')
            mhclo.clothes = clothes

        if not mhclo.verts or len(mhclo.verts.keys()) <1:
            raise ValueError('There is no vertex info in the MHCLO!?')

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

        mesh = mhclo.clothes.data
        assert isinstance(mesh, bpy.types.Mesh)

        edit_bmesh = None
        current_shape_settings = None
        current_active_object = bpy.context.view_layer.objects.active

        # If the mesh has shape keys, switch to edit mode to update.
        if mesh.shape_keys and len(mesh.shape_keys.key_blocks) > 0:
            bpy.context.view_layer.objects.active = mhclo.clothes

            current_shape_settings = (mhclo.clothes.active_shape_key_index,
                                      mhclo.clothes.use_shape_key_edit_mode,
                                      mhclo.clothes.show_only_shape_key)

            mhclo.clothes.active_shape_key_index = 0
            mhclo.clothes.use_shape_key_edit_mode = True
            mhclo.clothes.show_only_shape_key = True

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            assert mhclo.clothes.mode == 'EDIT'

            edit_bmesh = bmesh.from_edit_mesh(mesh)
            clothes_vertices = edit_bmesh.verts

        else:
            clothes_vertices = mesh.vertices

        _LOG.debug("About to try to match vertices: ", len(clothes_vertices))
        _LOG.dump("Verts", mhclo.verts)

        for clothes_vertex_number, clothes_vertex in enumerate(clothes_vertices):
            vertex_match_info = mhclo.verts[clothes_vertex_number]
            _LOG.dump("Vertex match info", (clothes_vertex_number, vertex_match_info))
            (human_vertex1, human_vertex2, human_vertex3) = vertex_match_info["verts"]

            # test if we inside mesh, if not, no chance
            #
            if human_vertex1 >= human_vertices_count or human_vertex2 > human_vertices_count or human_vertex3 >= human_vertices_count:
                continue

            offset = [vertex_match_info["offsets"][0]*x_size, vertex_match_info["offsets"][1]*z_size, vertex_match_info["offsets"][2]*y_size]
            clothes_vertex.co = \
                vertex_match_info["weights"][0] * human_vertices[human_vertex1].co + \
                vertex_match_info["weights"][1] * human_vertices[human_vertex2].co + \
                vertex_match_info["weights"][2] * human_vertices[human_vertex3].co + \
                Vector(offset)

        if edit_bmesh:
            bmesh.update_edit_mesh(mesh, destructive=False)

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            (mhclo.clothes.active_shape_key_index,
             mhclo.clothes.use_shape_key_edit_mode,
             mhclo.clothes.show_only_shape_key) = current_shape_settings

            bpy.context.view_layer.objects.active = current_active_object

        # We need to take into account that the base mesh might be rigged. If it is, we'll want the rig position
        # rather than the basemesh position
        if set_parent:
            if basemesh.parent:
                clothes.location = (0.0, 0.0, 0.0)
                clothes.parent = basemesh.parent
            else:
                clothes.location = basemesh.location

        # As we are finished with the combined shape key we can now remove it
        basemesh.shape_key_remove(shape_key)

    @staticmethod
    def _conservative_mask(basemesh, vertices_list):

        vertices_list.sort()

        _LOG.reset_timer()

        vertex_to_face = ObjectService.get_vertex_to_face_table()
        face_to_vertex = ObjectService.get_face_to_vertex_table()
        _LOG.time("loading tables")
        _LOG.reset_timer()

        relevant_faces = set()
        for vertex_index in vertices_list:
            for face_index in vertex_to_face[vertex_index]:
                relevant_faces.add(face_index)
        _LOG.time("extracting relevant faces")
        _LOG.reset_timer()

        partially_affected_faces = set()
        for face_index in relevant_faces:
            for vertex_index in face_to_vertex[face_index]:
                if not vertex_index in vertices_list:
                    partially_affected_faces.add(face_index)
                    break
        _LOG.time("finding faces with non-group vertices")
        _LOG.reset_timer()

        for face_index in partially_affected_faces:
            for vertex in face_to_vertex[face_index]:
                if vertex in vertices_list:
                    vertices_list.remove(vertex)

        _LOG.time("excluding vertices")

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
                    delete_vertices_list.append(int(vertex_to_delete))

            # Remove outliers
            ClothesService._conservative_mask(basemesh, delete_vertices_list)

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
    def find_clothes_absolute_path(clothes_object):
        asset_source = GeneralObjectProperties.get_value("asset_source", entity_reference=clothes_object)
        object_type = ObjectService.get_object_type(clothes_object).lower()
        _LOG.debug("asset source, object type", (asset_source, object_type))

        if asset_source and object_type:
            return AssetService.find_asset_absolute_path(asset_source, object_type)

    @staticmethod
    def interpolate_vertex_group_from_basemesh_to_clothes(basemesh, clothes_object, vertex_group_name, match_cutoff=0.3, mhclo_full_path=None):
        _LOG.enter()
        relevant_basemesh_vert_idxs = ObjectService.get_vertex_indexes_for_vertex_group(basemesh, vertex_group_name)
        _LOG.debug("Number of relevant basemesh vertices:", len(relevant_basemesh_vert_idxs))
        _LOG.dump("Relevant basemesh vertices", relevant_basemesh_vert_idxs)
        _LOG.debug("Supplied mhclo_full_path", mhclo_full_path)
        _LOG.debug("clothes_object", clothes_object)
        if not mhclo_full_path:
            mhclo_full_path = ClothesService.find_clothes_absolute_path(clothes_object)
        _LOG.debug("final mhclo full path", mhclo_full_path)

        new_vert_group = clothes_object.vertex_groups.new(name=vertex_group_name)

        mhclo = Mhclo()
        mhclo.load(mhclo_full_path)

        relevant_clothes_vert_idxs = []

        for clothes_vert_idx in mhclo.verts:
            mhclo_vert = mhclo.verts[clothes_vert_idx]
            _LOG.dump("mhclo_vert", (clothes_vert_idx, mhclo_vert))
            for match_vert in range(3):
                basemesh_vert_idx = mhclo_vert["verts"][match_vert]
                basemesh_vert_weight = mhclo_vert["weights"][match_vert]
                if basemesh_vert_idx in relevant_basemesh_vert_idxs:
                    if clothes_vert_idx not in relevant_clothes_vert_idxs:
                        relevant_clothes_vert_idxs.append(clothes_vert_idx)

        _LOG.debug("Number of matching vertices", len(relevant_clothes_vert_idxs))
        _LOG.dump("Relevant clothes idxs", relevant_clothes_vert_idxs)

        new_vert_group.add(relevant_clothes_vert_idxs, 1.0, 'ADD')

        return new_vert_group


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
            # Force interpolation of rigify deform groups or masks even if no bone in metarig
            if group.name.startswith("DEF-") or group.name.startswith("mhmask-"):
                clothes_weights[str(group.name)] = []

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
                            groups[idx] = 0
                        # Add the calculated weight to the list of found weights
                        #
                        # Human vertex group weight * Human vertex weight
                        groups[idx] += group.weight * assigned_weight

            # Iterate over all found vertex groups for the current clothes vertex
            # and calculcate the average weight for each group
            for idx in groups.keys():
                average_weight = groups[idx] / sum(clothes_vert["weights"])
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
    def set_up_rigging(basemesh, clothes, rig, mhclo, *,
                       interpolate_weights=True, import_subrig=True, import_weights=True):
        """Set up weights and a custom sub-rig for the given clothes object."""

        subrig = None

        if import_subrig:
            file_name = mhclo.basename + ".mpfbskel"

            if os.path.isfile(file_name):
                parent_rig = Rig.from_given_basemesh_and_armature(basemesh, rig, fast_positions=True)
                subrig_data = Rig.from_json_file_and_basemesh(file_name, clothes, parent=parent_rig)
                subrig = subrig_data.create_armature_and_fit_to_basemesh(add_modifier=False)

                subrig.name = subrig.data.name = clothes.name + ".rig"

                if mhclo.uuid:
                    GeneralObjectProperties.set_value("uuid", mhclo.uuid, entity_reference=subrig)

                ObjectService.activate_blender_object(clothes, deselect_all=True)

        if subrig:
            clothes.parent = subrig
            subrig.parent = rig
        else:
            clothes.parent = rig

        if interpolate_weights:
            ClothesService.interpolate_weights(basemesh, clothes, rig, mhclo)

        if import_weights:
            ClothesService.load_custom_weights(clothes, rig, subrig, mhclo)

        RigService.ensure_armature_modifier(clothes, rig, subrig=subrig)

    @staticmethod
    def load_custom_weights(clothes, armature_object, subrig, mhclo):
        """Try to load custom weights for the given clothes and rig."""

        armatures = [armature_object]
        if subrig:
            armatures.append(subrig)

        def try_load_weights(suffix, all=False):
            file_name = mhclo.get_weights_filename(suffix)

            if os.path.isfile(file_name):
                RigService.load_weights(armatures, clothes, file_name, all=all, replace=True)
                return True

        # Load groups matching bones from the common file.
        try_load_weights(None)

        # Load all groups - use for masks not matching the mhmask pattern.
        try_load_weights("force", all=True)

        # Load groups matching bones from the rig-specific file.
        rig_type = RigService.identify_rig(armature_object)
        rig_type = rig_type.replace("rigify_generated", "rigify")

        if "unknown" not in rig_type:
            for try_type in RigService.get_rig_weight_fallbacks(rig_type):
                if try_load_weights(try_type):
                    break

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

    @staticmethod
    def create_mhclo_from_clothes_matching(basemesh, clothes, properties_dict=None):
        """Create a MHCLO object by matching vertices on the clothes to vertices on the basemesh."""
        mhclo = Mhclo()
        mhclo.verts = dict()
        mhclo.clothes = clothes

        reference_scale = ClothesService.get_reference_scale(basemesh)

        if properties_dict:
            for key in properties_dict.keys():
                name = str(key)
                if hasattr(mhclo, name):
                    value = properties_dict[key]
                    setattr(mhclo, name, value)

        cache_dir = LocationService.get_user_cache("basemesh_xref")
        read_cache = os.path.exists(cache_dir)

        before = time.time()
        basemesh_xref = MeshCrossRef(basemesh, after_modifiers=True, build_faces_by_group_reference=True, cache_dir=cache_dir, write_cache=False, read_cache=read_cache)
        after = time.time()
        duration = int((after - before) * 1000.0)
        _LOG.debug("basemesh xref", (duration, basemesh_xref))

        before = time.time()
        clothes_xref = MeshCrossRef(clothes, after_modifiers=True, build_faces_by_group_reference=True, cache_dir=None, write_cache=False, read_cache=False)
        after = time.time()
        duration = int((after - before) * 1000.0)
        _LOG.debug("clothes xref", (duration, clothes_xref))

        scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=basemesh)

        max_pole = 0
        _LOG.debug("edges by vertex", clothes_xref.edges_by_vertex)
        for edges in clothes_xref.edges_by_vertex:
            _LOG.debug("edges", edges)
            if len(edges) > max_pole:
                max_pole = len(edges)

        if max_pole:
            mhclo.max_pole = max_pole

        before = time.time()
        for vert in range(len(clothes_xref.vertex_coordinates)):
            vmatch = VertexMatch(clothes, vert, clothes_xref, basemesh, basemesh_xref, scale_factor=scale_factor, reference_scale=reference_scale)
            _LOG.debug("vmatch mhclo", vmatch.mhclo_line)
            mhclo.verts[vert] = vmatch.mhclo_line
        after = time.time()
        duration = int((after - before) * 1000.0)
        _LOG.debug("vert matching total", duration)

        return mhclo

    @staticmethod
    def get_reference_scale(basemesh, body_part_reference="Torso"):
        """Get a reference scale from a basemesh object."""

        reference_scale = {
            "x_scale": 1.0,
            "y_scale": 1.0,
            "z_scale": 1.0
            }

        # Cannot have modifiers which alter the number of vertices
        mesh_object = basemesh.copy()
        mesh_object.data = basemesh.data.copy()
        ObjectService.link_blender_object(mesh_object)
        for modifier in mesh_object.modifiers:
            if modifier.type in ["MASK", "SUBSURF"]:
                mesh_object.modifiers.remove(modifier)

        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated_mesh = mesh_object.evaluated_get(depsgraph)
        mesh = evaluated_mesh.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

        dimensions = CLOTHES_REFERENCE_SCALE[body_part_reference]
        coords = dict()
        for key in dimensions.keys():
            vertex_index = dimensions[key]
            coords[key] = mesh.vertices[vertex_index].co

        reference_scale["x_scale"] = abs((coords["xmax"] - coords["xmin"]).length)
        reference_scale["y_scale"] = abs((coords["ymax"] - coords["ymin"]).length)
        reference_scale["z_scale"] = abs((coords["zmax"] - coords["zmin"]).length)

        basemesh_scale = 1.0
        scale_prop = GeneralObjectProperties.get_value("scale_factor", entity_reference=basemesh)
        if scale_prop:
            basemesh_scale = float(scale_prop)

        for key in reference_scale.keys():
            scale = reference_scale[key] / basemesh_scale
            if scale < 0.001:
                scale = 1.0
            reference_scale[key] = scale

        for key in dimensions.keys():
            reference_scale[key] = dimensions[key]

        evaluated_mesh.to_mesh_clear()
        ObjectService.delete_object(mesh_object)

        return reference_scale