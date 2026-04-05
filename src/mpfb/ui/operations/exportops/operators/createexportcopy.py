"""Functionality for creating an export copy of a character"""

from .....services import LogService
from .....services import ExportService
from .....services import FaceService
from .....services import ObjectService
from .....services import TargetService
from ....mpfboperator import MpfbOperator
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
import bpy

_LOG = LogService.get_logger("matops.createexportcopy")
_LOG.set_level(LogService.DEBUG)

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_Create_Export_Copy_Operator(MpfbOperator):
    """Create a deep copy of a character"""
    bl_idname = "mpfb.export_copy"
    bl_label = "Create export copy"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        from ..exportopspanel import EXPORTOPS_PROPERTIES  # pylint: disable=C0415
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=EXPORTOPS_PROPERTIES)

        if ctx.basemesh is None:
            self.report({'ERROR'}, "Could not deduce basemesh")
            return {'FINISHED'}

        _LOG.debug("settings", {
            "bake_shapekeys": ctx.bake_shapekeys,
            "remove_basemesh": ctx.remove_basemesh,
            "delete_helpers": ctx.delete_helpers,
            "suffix": ctx.suffix,
            "create_collection": ctx.collection,
            "visemes_meta": ctx.visemes_meta,
            "visemes_microsoft": ctx.visemes_microsoft,
            "faceunits_arkit": ctx.faceunits_arkit,
            "interpolate": ctx.interpolate,
            "mask_modifiers": ctx.mask_modifiers,
            "subdiv_modifiers": ctx.subdiv_modifiers})

        bake_masks = ctx.mask_modifiers == "BAKE"
        bake_subdiv = ctx.subdiv_modifiers == "BAKE"

        if ctx.collection:
            if "export copy" not in bpy.data.collections:
                collection = bpy.data.collections.new("export copy")
                bpy.context.scene.collection.children.link(collection)
            else:
                collection = bpy.data.collections["export copy"]
        else:
            collection = ctx.basemesh.users_collection[0]

        _LOG.debug("collection", collection)

        export_copy = ExportService.create_character_copy(ctx.basemesh, name_suffix=ctx.suffix, place_in_collection=collection)
        new_basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(export_copy)

        if ctx.bake_shapekeys:
            TargetService.bake_targets(new_basemesh)

        if ctx.visemes_meta or ctx.visemes_microsoft or ctx.faceunits_arkit:
            FaceService.load_targets(
                new_basemesh,
                load_microsoft_visemes=ctx.visemes_microsoft,
                load_meta_visemes=ctx.visemes_meta,
                load_arkit_faceunits=ctx.faceunits_arkit)

        if ctx.interpolate:
            FaceService.interpolate_targets(new_basemesh)

        ExportService.bake_modifiers_remove_helpers(
            new_basemesh,
            bake_masks=bake_masks,
            bake_subdiv=bake_subdiv,
            remove_helpers=ctx.delete_helpers,
            also_proxy=True)

        if ctx.mask_modifiers == "REMOVE":
            for modifier in new_basemesh.modifiers:
                if modifier.type == 'MASK':
                    # This will also remove modifiers which are unrelated to MPFB. This is intended.
                    new_basemesh.modifiers.remove(modifier)

        if ctx.subdiv_modifiers == "REMOVE":
            for modifier in new_basemesh.modifiers:
                if modifier.type == 'SUBSURF':
                    new_basemesh.modifiers.remove(modifier)

        if ctx.delete_helpers:
            context.view_layer.objects.active = new_basemesh

        if ctx.remove_basemesh:
            ObjectService.delete_object(new_basemesh)

        self.report({'INFO'}, "Export copy created")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Create_Export_Copy_Operator)
