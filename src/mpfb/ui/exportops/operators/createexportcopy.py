"""Functionality for creating an export copy of a character"""

from ....services import LogService
from ....services import ExportService
from ....services import ObjectService
from ....services import TargetService
from ...mpfboperator import MpfbOperator
from .... import ClassManager
import bpy

_LOG = LogService.get_logger("matops.createexportcopy")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_Create_Export_Copy_Operator(MpfbOperator):
    """Operation to create an export copy of a character"""
    bl_idname = "mpfb.export_copy"
    bl_label = "Create export copy"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        obj = context.object
        if not obj:
            return False
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            return False
        return True

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        scene = context.scene

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not deduce basemesh")
            return {'FINISHED'}

        from ..exportopspanel import EXPORTOPS_PROPERTIES
        bake_shapekeys = EXPORTOPS_PROPERTIES.get_value("bake_shapekeys", entity_reference=scene)
        remove_basemesh = EXPORTOPS_PROPERTIES.get_value("remove_basemesh", entity_reference=scene)
        delete_helpers = EXPORTOPS_PROPERTIES.get_value("delete_helpers", entity_reference=scene)
        suffix = EXPORTOPS_PROPERTIES.get_value("suffix", entity_reference=scene)
        create_collection = EXPORTOPS_PROPERTIES.get_value("collection", entity_reference=scene)
        visemes_meta = EXPORTOPS_PROPERTIES.get_value("visemes_meta", entity_reference=scene)
        visemes_microsoft = EXPORTOPS_PROPERTIES.get_value("visemes_microsoft", entity_reference=scene)
        faceunits_arkit = EXPORTOPS_PROPERTIES.get_value("faceunits_arkit", entity_reference=scene)
        interpolate = EXPORTOPS_PROPERTIES.get_value("interpolate", entity_reference=scene)
        mask_modifiers = EXPORTOPS_PROPERTIES.get_value("mask_modifiers", entity_reference=scene)
        subdiv_modifiers = EXPORTOPS_PROPERTIES.get_value("subdiv_modifiers", entity_reference=scene)

        _LOG.debug("settings", {
            "bake_shapekeys": bake_shapekeys,
            "remove_basemesh": remove_basemesh,
            "delete_helpers": delete_helpers,
            "suffix": suffix,
            "create_collection": create_collection,
            "visemes_meta": visemes_meta,
            "visemes_microsoft": visemes_microsoft,
            "faceunits_arkit": faceunits_arkit,
            "interpolate": interpolate,
            "mask_modifiers": mask_modifiers,
            "subdiv_modifiers": subdiv_modifiers})

        bake_masks = mask_modifiers == "BAKE"
        bake_subdiv = subdiv_modifiers == "BAKE"

        if create_collection:
            if "export copy" not in bpy.data.collections:
                collection = bpy.data.collections.new("export copy")
                bpy.context.scene.collection.children.link(collection)
            else:
                collection = bpy.data.collections["export copy"]
        else:
            collection = basemesh.users_collection[0]

        _LOG.debug("collection", collection)

        export_copy = ExportService.create_character_copy(basemesh, name_suffix=suffix, place_in_collection=collection)
        new_basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(export_copy)

        if bake_shapekeys:
            TargetService.bake_targets(new_basemesh)

        if visemes_meta or visemes_microsoft or faceunits_arkit:
            ExportService.load_targets(
                new_basemesh,
                load_microsoft_visemes=visemes_microsoft,
                load_meta_visemes=visemes_meta,
                load_arkit_faceunits=faceunits_arkit)

        if interpolate:
            ExportService.interpolate_targets(new_basemesh)

        ExportService.bake_modifiers_remove_helpers(
            new_basemesh,
            bake_masks=bake_masks,
            bake_subdiv=bake_subdiv,
            remove_helpers=delete_helpers,
            also_proxy=True)

        if mask_modifiers == "REMOVE":
            for modifier in new_basemesh.modifiers:
                if modifier.type == 'MASK':
                    # This will also remove modifiers which are unrelated to MPFB. This is intended.
                    new_basemesh.modifiers.remove(modifier)

        if subdiv_modifiers == "REMOVE":
            for modifier in new_basemesh.modifiers:
                if modifier.type == 'SUBSURF':
                    new_basemesh.modifiers.remove(modifier)

        if delete_helpers:
            context.view_layer.objects.active = new_basemesh

        if remove_basemesh:
            ObjectService.delete_object(new_basemesh)

        self.report({'INFO'}, "Export copy created")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Create_Export_Copy_Operator)
