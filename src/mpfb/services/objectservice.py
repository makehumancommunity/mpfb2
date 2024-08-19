"""This module contains utility functions for working with objects."""

import bpy, os, json, random, gzip, typing, string
from .logservice import LogService
from .locationservice import LocationService
from .systemservice import SystemService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.socketobject import BASEMESH_EXTRA_GROUPS

_LOG = LogService.get_logger("services.objectservice")

_BASEMESH_VERTEX_GROUPS_UNEXPANDED = None
_BASEMESH_VERTEX_GROUPS_EXPANDED = None

_BASEMESH_FACE_TO_VERTEX_TABLE = None
_BASEMESH_VERTEX_TO_FACE_TABLE = None

_BODY_PART_TYPES = ("Eyes", "Eyelashes", "Eyebrows", "Tongue", "Teeth", "Hair")
_MESH_ASSET_TYPES = ("Proxymeshes", "Clothes") + _BODY_PART_TYPES
_MESH_TYPES = ("Basemesh",) + _MESH_ASSET_TYPES
_SKELETON_TYPES = ("Skeleton", "Subrig")
_ALL_TYPES = _SKELETON_TYPES + _MESH_TYPES


class ObjectService:
    """ObjectService contains various functions for working with objects, such as creating a new object,
    identifying an object, finding an object an so forth."""

    def __init__(self):
        raise RuntimeError("You should not instance ObjectService. Use its static methods instead.")

    @staticmethod
    def random_name():
        """Generate a random string containing 15 lowercase ascii characters."""
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(15))

    @staticmethod
    def delete_object_by_name(name):
        """Safely delete an object with a given name. Will gracefully skip doing anything if the object does not exist."""
        if not name:
            return
        if not name in bpy.data.objects:
            return
        ObjectService.delete_object(bpy.data.objects[name])

    @staticmethod
    def delete_object(object_to_delete):
        """Safely delete an object with a given name. Will gracefully skip doing anything if the object is None."""
        if not object_to_delete:
            return
        bpy.data.objects.remove(object_to_delete, do_unlink=True)

    @staticmethod
    def object_name_exists(name):
        """Check if there's an existing object with the given name."""
        if not name:
            return False
        return name in bpy.data.objects

    @staticmethod
    def ensure_unique_name(desired_name):
        """Make sure that the name is unique. If no object with the given name exists, return the name unchanged.
        Otherwise add an incrementing number to the name until there's no name clash."""
        if not ObjectService.object_name_exists(desired_name):
            return desired_name
        for i in range(1, 100):
            ranged_name = desired_name + "." + str(i).zfill(3)
            if not ObjectService.object_name_exists(ranged_name):
                return ranged_name
        return desired_name + ".999"

    @staticmethod
    def activate_blender_object(object_to_make_active, *, context=None, deselect_all=False):
        """Make given object selected and active. Optionally also deselect all other objects."""
        if deselect_all:
            ObjectService.deselect_and_deactivate_all()

        object_to_make_active.select_set(True)

        context = context or bpy.context
        context.view_layer.objects.active = object_to_make_active

    @staticmethod
    def deselect_and_deactivate_all():
        """Make sure no object is selected nor active."""
        if bpy.context.object:
            try:
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.context.object.select_set(False)
            except:
                _LOG.debug("Tried mode_set / unselect on non-existing object")
        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj
            bpy.context.active_object.select_set(False)
            obj.select_set(False)
        bpy.context.view_layer.objects.active = None

    @staticmethod
    def has_vertex_group(blender_object, vertex_group_name):
        if not blender_object or not vertex_group_name:
            return False
        for group in blender_object.vertex_groups:
            if group.name == vertex_group_name:
                return True
        return False

    @staticmethod
    def get_vertex_indexes_for_vertex_group(blender_object, vertex_group_name):
        if not blender_object or not vertex_group_name:
            return []
        group_index = None
        for group in blender_object.vertex_groups:
            if group.name == vertex_group_name:
                group_index = group.index
        if group_index is None:
            return []
        relevant_vertices = []
        for vertex in blender_object.data.vertices:
            for group in vertex.groups:
                if group.group == group_index:
                    if not vertex.index in relevant_vertices:
                        relevant_vertices.append(vertex.index)
        return relevant_vertices

    @staticmethod
    def create_blender_object_with_mesh(name="NewObject", parent=None, skip_linking=False):
        """Create a new mesh object with a mesh data block."""
        mesh = bpy.data.meshes.new(name + "Mesh")
        obj = bpy.data.objects.new(name, mesh)
        if not skip_linking:
            ObjectService.link_blender_object(obj, parent=parent)
        return obj

    @staticmethod
    def create_blender_object_with_armature(name="NewObject", parent=None):
        """Create a new armature object with an armature data block."""
        armature = bpy.data.armatures.new(name + "Armature")
        obj = bpy.data.objects.new(name, armature)
        ObjectService.link_blender_object(obj, parent=parent)
        return obj

    @staticmethod
    def create_empty(name, empty_type="SPHERE", parent=None):
        """Create a new empty object, optionally specifying its draw type and parent."""
        empty = bpy.data.objects.new(name=name, object_data=None)
        ObjectService.link_blender_object(empty, parent=parent)
        empty.empty_display_type = empty_type
        return empty

    @staticmethod
    def link_blender_object(object_to_link, collection=None, parent=None):
        """Link a blender object to a collection, optionally also assigning a parent object"""
        if collection is None:
            collection = bpy.context.collection
        collection.objects.link(object_to_link)
        _LOG.debug("object_to_link", object_to_link)
        _LOG.debug("parent", parent)
        if parent:
            object_to_link.parent = parent

    @staticmethod
    def get_list_of_children(parent_object):
        """Return list with objects whose parent property is set to parent_object."""
        children = []
        for potential_child in bpy.data.objects:
            if potential_child.parent == parent_object:
                children.append(potential_child)
        return children

    @staticmethod
    def find_by_data(id_data):
        for obj in bpy.data.objects:
            if obj.data == id_data:
                return obj
        return None

    @staticmethod
    def get_selected_objects(exclude_non_mh_objects=False, exclude_mesh_objects=False, exclude_armature_objects=False, exclude_meta_objects=True):
        """Find all selected objects, but optionally exclude non-MH objects, mesh objects, armature objects, and meta objects."""
        objects = []
        for object in bpy.context.selected_objects:
            include = True
            if object.type == "MESH" and exclude_mesh_objects:
                include = False
            if object.type == "ARMATURE" and exclude_armature_objects:
                include = False
            if object.type not in ["MESH", "ARMATURE"] and exclude_meta_objects:
                include = False
            if not ObjectService.get_object_type(object) and exclude_non_mh_objects:
                include = False
            if include:
                objects.append(object)
        return objects

    @staticmethod
    def get_selected_armature_objects():
        """Find all selected armature objects."""
        objects = []
        for object in bpy.context.selected_objects:
            if object.type == "ARMATURE":
                objects.append(object)
        return objects

    @staticmethod
    def get_selected_mesh_objects():
        """Find all selected mesh objects."""
        objects = []
        for object in bpy.context.selected_objects:
            if object.type == "MESH":
                objects.append(object)
        return objects

    @staticmethod
    def get_object_type(blender_object) -> str:
        """Return the value of the object_type custom property. This is a string which can be, for example,
        "Basemesh" for a human object."""
        if not blender_object:
            return ""

        object_type = GeneralObjectProperties.get_value("object_type", entity_reference=blender_object)

        return str(object_type or "").strip()

    @staticmethod
    def object_is(blender_object, mpfb_type_name: str | typing.Sequence[str]):
        """
        Check if the given object is of the correct type(s).

        Args:
            blender_object: Object to test
            mpfb_type_name: Type name, or list/tuple of acceptable type names.
        """

        if not mpfb_type_name:
            return False

        mpfb_type = ObjectService.get_object_type(blender_object)

        if not mpfb_type:
            return False

        mpfb_type = mpfb_type.lower()

        if isinstance(mpfb_type_name, str):
            mpfb_type_name = [mpfb_type_name]

        for item in mpfb_type_name:
            stripped = str(item).lower().strip()
            if stripped and stripped in mpfb_type:
                return True

        if mpfb_type_name is _ALL_TYPES:
            # This is supposed to handle all possible types.
            _LOG.debug("Unexpected object type: " + mpfb_type)

        return False

    @staticmethod
    def object_is_basemesh(blender_object):
        """Object has object_type == Basemesh"""
        return ObjectService.object_is(blender_object, "Basemesh")

    @staticmethod
    def object_is_skeleton(blender_object):
        return ObjectService.object_is(blender_object, "Skeleton")

    @staticmethod
    def object_is_subrig(blender_object):
        return ObjectService.object_is(blender_object, "Subrig")

    @staticmethod
    def object_is_any_skeleton(blender_object):
        return ObjectService.object_is(blender_object, _SKELETON_TYPES)

    @staticmethod
    def object_is_body_proxy(blender_object):
        """Object has object_type Proxymesh or Proxymeshes."""
        return ObjectService.object_is(blender_object, "Proxymesh") or ObjectService.object_is(blender_object, "Proxymeshes")

    @staticmethod
    def object_is_eyes(blender_object):
        """Object has object_type == Eyes."""
        return ObjectService.object_is(blender_object, "Eyes")

    @staticmethod
    def object_is_basemesh_or_body_proxy(blender_object):
        """Object has object_type Basemesh or Proxymesh."""
        return ObjectService.object_is_basemesh(blender_object) or ObjectService.object_is_body_proxy(blender_object)

    @staticmethod
    def object_is_any_mesh(blender_object):
        """Object is not none and has type MESH."""
        return blender_object and blender_object.type == "MESH"

    @staticmethod
    def object_is_any_makehuman_mesh(blender_object):
        """Object is not none, has type MESH and has a valid object_type set."""
        return blender_object and blender_object.type == "MESH" and ObjectService.get_object_type(blender_object)

    @staticmethod
    def object_is_any_mesh_asset(blender_object):
        """Object is not none, has type MESH and has an object_type set which is listed as a mesh asset."""
        return blender_object and blender_object.type == "MESH" and\
            ObjectService.object_is(blender_object, _MESH_ASSET_TYPES)

    @staticmethod
    def object_is_any_makehuman_object(blender_object):
        """Object is not none and has a valid object_type set."""
        return blender_object and ObjectService.get_object_type(blender_object)

    @staticmethod
    def find_object_of_type_amongst_nearest_relatives(
            blender_object: bpy.types.Object,
            mpfb_type_name: str | typing.Sequence[str]="Basemesh", *,
            only_parents=False, strict_parent=False, only_children=False,
            ) -> typing.Optional[bpy.types.Object]:
        """
        Find one object of the given type(s) among the children, parents and siblings of the object.
        """
        relatives = ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, mpfb_type_name,
            only_parents=only_parents, strict_parent=strict_parent, only_children=only_children)

        return next(relatives, None)

    @staticmethod
    def find_all_objects_of_type_amongst_nearest_relatives(
            blender_object: bpy.types.Object,
            mpfb_type_name: str | typing.Sequence[str]="Basemesh", *,
            only_parents=False, strict_parent=False, only_children=False,
            ) -> typing.Generator[bpy.types.Object, None, None]:
        """
        Find all objects of the given type(s) among the children, parents and siblings of the object.

        Args:
            blender_object: Object to start search from.
            mpfb_type_name: String or sequence of strings denoting valid types.
            only_parents: Only search among the object and its parents.
            strict_parent: Don't search immediate siblings if the parent isn't a MakeHuman object.
            only_children: Only search among the object and its children.
        """

        if not blender_object or not mpfb_type_name:
            return

        def rec_children(rec_parent, exclude=None):
            if only_parents:
                return

            for parents_child in ObjectService.get_list_of_children(rec_parent):
                if parents_child == exclude:
                    continue

                if ObjectService.object_is(parents_child, mpfb_type_name):
                    yield parents_child
                elif parents_child.type == "ARMATURE":
                    yield from rec_children(parents_child)

        if ObjectService.object_is(blender_object, mpfb_type_name):
            yield blender_object

        yield from rec_children(blender_object)

        if only_children:
            return

        parent_from = blender_object
        parent = blender_object.parent

        while parent:
            if strict_parent:
                if parent.type != 'ARMATURE' and not ObjectService.object_is_any_makehuman_object(parent):
                    break

            if ObjectService.object_is(parent, mpfb_type_name):
                yield parent

            yield from rec_children(parent, parent_from)

            parent_from = parent
            parent = parent.parent
            strict_parent = True

    @staticmethod
    def find_related_objects(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _ALL_TYPES, **kwargs)

    @staticmethod
    def find_related_skeletons(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _SKELETON_TYPES, **kwargs)

    @staticmethod
    def find_related_mesh_base_or_assets(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _MESH_TYPES, **kwargs)

    @staticmethod
    def find_related_mesh_assets(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _MESH_ASSET_TYPES, **kwargs)

    @staticmethod
    def find_related_body_part_assets(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _BODY_PART_TYPES, **kwargs)

    @staticmethod
    def find_deformed_child_meshes(armature_object) -> typing.Generator[bpy.types.Object, None, None]:
        if not armature_object:
            return

        assert armature_object.type == 'ARMATURE'

        for child in ObjectService.get_list_of_children(armature_object):
            if child.type == 'MESH':
                for mod in child.modifiers:
                    if mod.type == 'ARMATURE' and mod.object == armature_object:
                        yield child

    @staticmethod
    def object_is_generated_rigify_rig(blender_object):
        return blender_object and blender_object.type == "ARMATURE" and blender_object.data.get("rig_id")

    @staticmethod
    def object_is_rigify_metarig(blender_object, *, check_bones=False):
        if not blender_object or blender_object.type != "ARMATURE" or blender_object.data.get("rig_id"):
            return False

        if (blender_object.data.get("rigify_target_rig") or
                blender_object.data.get("rigify_colors") and len(blender_object.data.rigify_colors) > 0 or
                any(bcoll.get("rigify_ui_row", 0) > 0 for bcoll in blender_object.data.collections)):
            return True

        if check_bones:
            for bone in blender_object.pose.bones:
                if bone.get("rigify_type"):
                    return True

        return False

    @staticmethod
    def find_rigify_metarig_by_rig(blender_object):
        if not ObjectService.object_is_generated_rigify_rig(blender_object):
            return None

        for obj in bpy.data.objects:
            if obj.type == "ARMATURE" and obj.data.get("rigify_target_rig") == blender_object:
                return obj
        return None

    @staticmethod
    def find_rigify_rig_by_metarig(blender_object):
        if not blender_object or blender_object.type != "ARMATURE" or blender_object.data.get("rig_id"):
            return None

        return blender_object.data.get("rigify_target_rig", None)

    @staticmethod
    def find_armature_context_objects(
            armature_object: bpy.types.Object | None, *, operator=None,
            is_subrig: bool | None=None, only_basemesh=False,
            ) -> tuple[bpy.types.Object | None, bpy.types.Object | None, bpy.types.Object | None]:
        """
        Find base rig, basemesh, and directly controlled mesh (same as basemesh unless subrig) for the given rig.
        When searching for meshes, automatically jumps from rigify metarigs to the generated rig when necessary.
        To determine success, check direct_mesh for None.
        """

        if not armature_object:
            if operator:
                operator.report({'ERROR'}, "Could not find the armature object.")
            return None, None, None

        assert isinstance(armature_object, bpy.types.Object) and armature_object.type == 'ARMATURE'

        if is_subrig is False:
            # When explicitly defining the rig status as non-subrig, use it as the skeleton
            base_rig = armature_object
        else:
            base_rig = ObjectService.find_object_of_type_amongst_nearest_relatives(
                armature_object, mpfb_type_name="Skeleton", only_parents=True)

        if base_rig is None:
            if operator:
                operator.report(
                    {'ERROR'}, "Could not find related main skeleton. It should have been a parent of the armature.")

            return None, None, None

        else:
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(
                base_rig, mpfb_type_name="Basemesh", only_children=True)

            if not basemesh:
                basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(
                    ObjectService.find_rigify_rig_by_metarig(base_rig),
                    mpfb_type_name="Basemesh", only_children=True)

            if only_basemesh:
                direct_mesh = None

            elif basemesh is None:
                if operator:
                    operator.report({'ERROR'},
                                    "Could not find related base mesh. "
                                    "It should have been a sibling or child of the armature.")

                direct_mesh = None

            else:
                if is_subrig is None:
                    is_subrig = ObjectService.object_is_subrig(armature_object)

                if is_subrig:
                    child_meshes = list(ObjectService.find_deformed_child_meshes(armature_object))

                    if not child_meshes:
                        child_meshes = list(ObjectService.find_deformed_child_meshes(
                            ObjectService.find_rigify_rig_by_metarig(armature_object)))

                    if len(child_meshes) != 1:
                        if operator:
                            operator.report({'ERROR'},
                                            "Could not find a unique deformed clothing mesh. "
                                            "It should be a child of the armature.")
                        direct_mesh = None
                    else:
                        direct_mesh = child_meshes[0]
                else:
                    if base_rig != armature_object:
                        if operator:
                            operator.report({'ERROR'}, "The armature is neither a sub-rig nor main skeleton.")
                        direct_mesh = None
                    else:
                        direct_mesh = basemesh

            return base_rig, basemesh, direct_mesh

    @staticmethod
    def load_wavefront_file(filepath, context=None):
        if context is None:
            context = bpy.context
        if filepath is None:
            raise ValueError('Cannot load None filepath')
        if not os.path.exists(filepath):
            raise IOError('File does not exist: ' + filepath)

        bpy.ops.wm.obj_import(filepath=filepath, use_split_objects=False, use_split_groups=False)

        # previous blender operation: bpy.ops.import_scene.obj(filepath=filepath, use_split_objects=False, use_split_groups=False)

        # import_scene rotated object 90 degrees
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        loaded_object = context.selected_objects[0]  # pylint: disable=E1136
        return loaded_object

    @staticmethod
    def save_wavefront_file(filepath, mesh_object, context=None):
        if context is None:
            context = bpy.context
        if filepath is None:
            raise ValueError('Cannot load None filepath')
        if not mesh_object or mesh_object.type != 'MESH':
            raise ValueError('No valid mesh object was provided')

        ObjectService.deselect_and_deactivate_all()
        mesh_object.select_set(True)

        bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True, export_materials=False)

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
        global _BASEMESH_VERTEX_GROUPS_EXPANDED  # pylint: disable=W0603
        global _BASEMESH_VERTEX_GROUPS_UNEXPANDED  # pylint: disable=W0603
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
                    _BASEMESH_VERTEX_GROUPS_EXPANDED[group_name].extend(range(start_stop[0], start_stop[1] + 1))
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

    @staticmethod
    def get_face_to_vertex_table():
        global _BASEMESH_FACE_TO_VERTEX_TABLE  # pylint: disable=W0603

        meta_data_dir = LocationService.get_mpfb_data("mesh_metadata")
        definition_file = os.path.join(meta_data_dir, "basemesh_face_to_vertex_table.json.gz")

        if _BASEMESH_FACE_TO_VERTEX_TABLE is None:
            with gzip.open(definition_file, "rb") as json_file:
                _BASEMESH_FACE_TO_VERTEX_TABLE = json.load(json_file)

        return _BASEMESH_FACE_TO_VERTEX_TABLE

    @staticmethod
    def get_vertex_to_face_table():
        global _BASEMESH_VERTEX_TO_FACE_TABLE  # pylint: disable=W0603

        meta_data_dir = LocationService.get_mpfb_data("mesh_metadata")
        definition_file = os.path.join(meta_data_dir, "basemesh_vertex_to_face_table.json.gz")

        if _BASEMESH_VERTEX_TO_FACE_TABLE is None:
            with gzip.open(definition_file, "rb") as json_file:
                _BASEMESH_VERTEX_TO_FACE_TABLE = json.load(json_file)

        return _BASEMESH_VERTEX_TO_FACE_TABLE

    @staticmethod
    def extract_vertex_group_to_new_object(existing_object, vertex_group_name):

        clothes_obj = existing_object.copy()
        clothes_obj.data = clothes_obj.data.copy()
        clothes_obj.parent = None
        clothes_obj.animation_data_clear()
        clothes_obj.name = "clothes"
        bpy.context.collection.objects.link(clothes_obj)

        for modifier in clothes_obj.modifiers:
            clothes_obj.modifiers.remove(modifier)

        for vgroup in clothes_obj.vertex_groups:
            if vertex_group_name != vgroup.name:
                clothes_obj.vertex_groups.remove(vgroup)

        existing_object.select_set(False)
        clothes_obj.select_set(True)
        bpy.context.view_layer.objects.active = clothes_obj

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        from .materialservice import MaterialService  # To avoid circular import
        MaterialService.delete_all_materials(clothes_obj)

        GeneralObjectProperties.set_value("asset_source", "", entity_reference=clothes_obj)
        GeneralObjectProperties.set_value("object_type", "Clothes", entity_reference=clothes_obj)

        key_name = "temporary_fitting_key." + str(random.randrange(1000, 9999))
        clothes_obj.shape_key_add(name=key_name, from_mix=True)
        print(len(clothes_obj.data.shape_keys.key_blocks))

        for name in clothes_obj.data.shape_keys.key_blocks.keys():
            if name != key_name and name != "Basis":
                shape_key = clothes_obj.data.shape_keys.key_blocks[name]
                clothes_obj.shape_key_remove(shape_key)

        if "Basis" in clothes_obj.data.shape_keys.key_blocks.keys():
            shape_key = clothes_obj.data.shape_keys.key_blocks["Basis"]
            clothes_obj.shape_key_remove(shape_key)

        shape_key = clothes_obj.data.shape_keys.key_blocks[key_name]
        clothes_obj.shape_key_remove(shape_key)
