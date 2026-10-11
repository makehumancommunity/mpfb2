# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025 - updated 6.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for deleting hair asset and removing its properties
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ...pollstrategy import pollstrategy, PollStrategy
from ..hairproperties import HAIR_PROPERTIES, FUR_PROPERTIES, CARDS_MODIFIER_NAME, CARDS_OBJECT_SUFFIX, \
    baked_image_names, forget_cards_settings
from .toggle_section_operator import forget_asset as forget_section_folds

import bpy

_LOG = LogService.get_logger("haireditorpanel.delete_hair_operator")

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_DeleteHair_Operator(MpfbOperator):
    """Deletes hair asset and removes all properties"""
    bl_idname = "mpfb.delete_hair_operator"
    bl_label = "Delete hair"
    bl_options = {'REGISTER', 'UNDO'}

    hair_asset: bpy.props.StringProperty()
    is_fur: bpy.props.BoolProperty(default=False)

    def get_logger(self):
        return _LOG

    def _remove_if_unused(self, collection, datablock):
        """Remove a datablock, unless something else in the scene is still referring to it."""
        if datablock is None:
            return
        if datablock.users > 0:
            _LOG.debug("Keeping datablock which is still in use", datablock.name)
            return
        collection.remove(datablock)

    def _remove_object_data(self, datablock):
        """Remove the geometry of a deleted object, blender leaves it behind as an orphan."""
        if isinstance(datablock, bpy.types.Mesh):
            self._remove_if_unused(bpy.data.meshes, datablock)
        elif isinstance(datablock, bpy.types.Curves):
            self._remove_if_unused(bpy.data.hair_curves, datablock)
        elif isinstance(datablock, bpy.types.Curve):
            self._remove_if_unused(bpy.data.curves, datablock)

    def _collect_dependencies(self, node_tree, node_group_names, image_names):
        """Note down every node group and image a node tree relies on, however deeply nested."""
        if node_tree is None:
            return
        for node in node_tree.nodes:
            image = getattr(node, "image", None)
            if image is not None:
                image_names.add(image.name)
            group = getattr(node, "node_tree", None)
            if group is not None and group.name not in node_group_names:
                node_group_names.add(group.name)
                self._collect_dependencies(group, node_group_names, image_names)

    def _purge_node_groups(self, node_group_names, image_names):
        """Remove the listed node groups which nothing uses any longer, repeated since removal orphans nested groups."""
        while True:
            removed_something = False
            for name in sorted(node_group_names):
                node_group = bpy.data.node_groups.get(name)
                if node_group is None or node_group.users > 0:
                    continue
                self._collect_dependencies(node_group, node_group_names, image_names)
                bpy.data.node_groups.remove(node_group)
                removed_something = True
            if not removed_something:
                return

    def hardened_execute(self, context):
        _LOG.enter()

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'CANCELLED'}

        card_name = f"{self.hair_asset}{CARDS_OBJECT_SUFFIX}"
        brace_name = f"{self.hair_asset}_brace"

        hair_obj = None
        objects_to_delete = []
        for child in ObjectService.get_list_of_children(basemesh):
            if child.name == self.hair_asset:
                hair_obj = child
            if child.name in [self.hair_asset, card_name, brace_name]:
                objects_to_delete.append(child)

        if hair_obj is None:
            self.report({'WARNING'}, f"Hair object '{self.hair_asset}' not found, only cleaning up its properties")

        object_data = [obj.data for obj in objects_to_delete]

        # Every asset has its own copies of the grooming node groups, tracked by name since the datablocks may be gone later
        node_group_names = {f"{card_name}_{CARDS_MODIFIER_NAME}"}
        # Includes the extra baked maps (normal, AO, ...)
        image_names = set(baked_image_names(self.hair_asset))
        materials = set()
        for obj in objects_to_delete:
            for modifier in obj.modifiers:
                node_group = getattr(modifier, "node_group", None)
                if node_group is not None:
                    node_group_names.add(node_group.name)
                    self._collect_dependencies(node_group, node_group_names, image_names)
            # Materials are taken from the objects, not looked up by name, as blender may rename them to "<asset>.001"
            for slot in obj.material_slots:
                if slot.material is not None:
                    materials.add(slot.material)

        # The hair shader is a node group nested inside the asset material
        for material in materials:
            self._collect_dependencies(material.node_tree, node_group_names, image_names)

        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)
        for datablock in object_data:
            self._remove_object_data(datablock)

        properties = FUR_PROPERTIES if self.is_fur else HAIR_PROPERTIES
        removed = properties.remove_dynamic_keys_with_prefix(f"{self.hair_asset}_", basemesh)
        _LOG.debug("Removed properties", removed)

        # Card settings are a plain custom property, so the sweep above does not remove them
        forget_cards_settings(basemesh, self.hair_asset)
        # Panel fold state is kept in a module dict, not on the character
        forget_section_folds(self.hair_asset)

        for material in materials:
            self._remove_if_unused(bpy.data.materials, material)

        self._purge_node_groups(node_group_names, image_names)

        for name in image_names:
            image = bpy.data.images.get(name)
            if image is not None:
                # Baked extra maps have a fake user, release it
                image.use_fake_user = False
            self._remove_if_unused(bpy.data.images, image)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        self.report({'INFO'}, f"Deleted hair asset '{self.hair_asset}'")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_DeleteHair_Operator)
