import bpy, os
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.entities.objectproperties import GeneralObjectProperties

_LOG = LogService.get_logger("services.objectservice")

# create object
# activate object
# select object
# deselect object
# deselect all objects
# find object by name

# add mask modifier
# add subdivision modifier

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
    def create_empty(name, type="SPHERE", parent=None):
        empty = bpy.data.objects.new(name=name, object_data=None)
        ObjectService.link_blender_object(empty, parent=parent)
        empty.empty_display_type = type
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
        bpy.ops.import_scene.obj(filepath=filepath, use_groups_as_vgroups=True)
        return context.active_object

    @staticmethod
    def load_base_mesh(context=None):
        objsdir = LocationService.get_mpfb_data("3dobjs")
        filepath = os.path.join(objsdir, "base.obj")
        return ObjectService.load_wavefront_file(filepath, context)
