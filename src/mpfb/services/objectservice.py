import bpy, os, json, random
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.socketobject import BASEMESH_EXTRA_GROUPS

_LOG = LogService.get_logger("services.objectservice")

_BASEMESH_VERTEX_GROUPS_UNEXPANDED = None
_BASEMESH_VERTEX_GROUPS_EXPANDED = None

class ObjectService:

    def __init__(self):
        raise RuntimeError("You should not instance ObjectService. Use its static methods instead.")

    @staticmethod
    def has_vertex_group(blender_object, vertex_group_name):
        if not blender_object or not vertex_group_name:
            return False
        for group in blender_object.vertex_groups:
            if group.name == vertex_group_name:
                return True
        return False

    @staticmethod
    def create_blender_object_with_mesh(name="NewObject"):
        mesh = bpy.data.meshes.new(name + "Mesh")
        obj = bpy.data.objects.new(name, mesh)
        return obj

    @staticmethod
    def create_empty(name, empty_type="SPHERE", parent=None):
        empty = bpy.data.objects.new(name=name, object_data=None)
        ObjectService.link_blender_object(empty, parent=parent)
        empty.empty_display_type = empty_type
        return empty

    @staticmethod
    def link_blender_object(object_to_link, collection=None, parent=None):
        if collection is None:
            collection = bpy.context.collection
        collection.objects.link(object_to_link)
        _LOG.debug("object_to_link", object_to_link)
        _LOG.debug("parent", parent)
        if parent:
            object_to_link.parent = parent

    @staticmethod
    def activate_blender_object(object_to_make_active):
        bpy.context.view_layer.objects.active = object_to_make_active

    @staticmethod
    def get_list_of_children(parent_object):
        children = []
        for potential_child in bpy.data.objects:
            if potential_child.parent == parent_object:
                children.append(potential_child)
        return children

    @staticmethod
    def object_is(blender_object, mpfb_type_name):
        if not blender_object:
            return False
        if not mpfb_type_name or not str(mpfb_type_name).strip():
            return False

        mpfb_type = GeneralObjectProperties.get_value("object_type", entity_reference=blender_object)

        if not mpfb_type:
            return False

        return str(mpfb_type_name).lower().strip() in str(mpfb_type).lower().strip()

    @staticmethod
    def object_is_basemesh(blender_object):
        return ObjectService.object_is(blender_object, "Basemesh")

    @staticmethod
    def object_is_skeleton(blender_object):
        return ObjectService.object_is(blender_object, "Skeleton")

    @staticmethod
    def object_is_body_proxy(blender_object):
        return ObjectService.object_is(blender_object, "Proxymesh")

    @staticmethod
    def object_is_basemesh_or_body_proxy(blender_object):
        return ObjectService.object_is(blender_object, "Basemesh") or ObjectService.object_is(blender_object, "Proxymesh")

    @staticmethod
    def find_object_of_type_amongst_nearest_relatives(blender_object, mpfb_type_name="Basemesh"):

        if not blender_object or not mpfb_type_name:
            return None

        type_name = str(mpfb_type_name).strip()

        if ObjectService.object_is(blender_object, type_name):
            return blender_object

        parent = blender_object.parent
        if parent:
            if ObjectService.object_is(parent, type_name):
                return parent
            for parents_child in ObjectService.get_list_of_children(parent):
                if ObjectService.object_is(parents_child, type_name):
                    return parents_child

        for objects_child in ObjectService.get_list_of_children(blender_object):
            if ObjectService.object_is(objects_child, type_name):
                return objects_child

        return None

    @staticmethod
    def load_wavefront_file(filepath, context=None):
        if context is None:
            context = bpy.context
        if filepath is None:
            raise ValueError('Cannot load None filepath')
        if not os.path.exists(filepath):
            raise IOError('File does not exist: ' + filepath)
        bpy.ops.import_scene.obj(filepath=filepath, use_split_objects=False, use_split_groups=False)

        # import_scene rotated object 90 degrees
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        loaded_object = bpy.context.selected_objects[0] # pylint: disable=E1136
        return loaded_object

    @staticmethod
    def load_base_mesh(context=None, scale_factor=1.0, load_vertex_groups=True, exclude_vertex_groups=None):
        objsdir = LocationService.get_mpfb_data("3dobjs")
        filepath = os.path.join(objsdir, "base.obj")
        basemesh = ObjectService.load_wavefront_file(filepath, context)
        basemesh.name = "Human"
        bpy.ops.object.shade_smooth()
        bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
        bpy.ops.object.transform_apply(scale=True)
        GeneralObjectProperties.set_value("object_type", "Basemesh", entity_reference=basemesh)
        GeneralObjectProperties.set_value("scale_factor", scale_factor, entity_reference=basemesh)
        if load_vertex_groups:
            groups = ObjectService.get_base_mesh_vertex_group_definition()
            ObjectService.assign_vertex_groups(basemesh, groups, exclude_vertex_groups)
        return basemesh

    @staticmethod
    def assign_vertex_groups(blender_object, vertex_group_definition, exclude_groups=None):
        if exclude_groups is None:
            exclude_groups = []
        for group_name in vertex_group_definition.keys():
            if group_name not in exclude_groups:
                vertex_group = blender_object.vertex_groups.new(name=group_name)
                vertex_group.add(vertex_group_definition[group_name], 1.0, 'ADD')

    @staticmethod
    def get_base_mesh_vertex_group_definition():
        global _BASEMESH_VERTEX_GROUPS_EXPANDED # pylint: disable=W0603
        global _BASEMESH_VERTEX_GROUPS_UNEXPANDED # pylint: disable=W0603
        if _BASEMESH_VERTEX_GROUPS_EXPANDED is None:
            meta_data_dir = LocationService.get_mpfb_data("mesh_metadata")
            definition_file = os.path.join(meta_data_dir, "basemesh_vertex_groups.json")
            with open(definition_file, "r") as json_file:
                _BASEMESH_VERTEX_GROUPS_UNEXPANDED = json.load(json_file)
            _BASEMESH_VERTEX_GROUPS_EXPANDED = dict()
            for group in _BASEMESH_VERTEX_GROUPS_UNEXPANDED.keys():
                group_name = str(group)
                _BASEMESH_VERTEX_GROUPS_EXPANDED[group_name] = []
                for start_stop in _BASEMESH_VERTEX_GROUPS_UNEXPANDED[group]:
                    _BASEMESH_VERTEX_GROUPS_EXPANDED[group_name].extend(range(start_stop[0], start_stop[1]))
            _BASEMESH_VERTEX_GROUPS_EXPANDED.update(BASEMESH_EXTRA_GROUPS)
        # Return a copy so it doesn't get accidentally modified
        return dict(_BASEMESH_VERTEX_GROUPS_EXPANDED)

    @staticmethod
    def get_lowest_point(basemesh, take_shape_keys_into_account=True):
        lowest_point = 1000.0
        vertex_data = basemesh.data.vertices
        shape_key = None
        key_name = None
        if take_shape_keys_into_account and basemesh.data.shape_keys and basemesh.data.shape_keys.key_blocks and len(basemesh.data.shape_keys.key_blocks) > 0:
            from .targetservice import TargetService
            key_name = "temporary_lowest_point_key." + str(random.randrange(1000, 9999))
            shape_key = TargetService.create_shape_key(basemesh, key_name, also_create_basis=True, create_from_mix=True)
            vertex_data = shape_key.data

        index = 0
        for vertex in vertex_data:
            if vertex.co[2] < lowest_point and index < 13380:
                lowest_point = vertex.co[2]
            index = index + 1

        if shape_key:
            basemesh.shape_key_remove(shape_key)

        return lowest_point
