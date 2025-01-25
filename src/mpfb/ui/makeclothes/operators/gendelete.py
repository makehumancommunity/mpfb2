"""Operator for generating a delete group."""

import bpy, os, re
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import LocationService
from ....services import ObjectService
from ....services import ClothesService
from ....services import AssetService
from ...makeclothes import MakeClothesObjectProperties
from ....entities.objectproperties import GeneralObjectProperties
from .... import ClassManager

_LOG = LogService.get_logger("makeclothes.gendelete")


class MPFB_OT_GenDeleteOperator(bpy.types.Operator):
    """Create a (very) rough delete group on the base mesh based on which vertices are matched by the clothes. You will need to edit this manually afterwards as it is most likely patchy and too large"""
    bl_idname = "mpfb.makeclothes_gendelete"
    bl_label = "Interpolate"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return context.active_object.type == "MESH"
        return False

    def execute(self, context):

        basemesh = None
        clothes = None
        for obj in context.selected_objects:
            if ObjectService.object_is_basemesh(obj):
                basemesh = obj
            else:
                ot = ObjectService.get_object_type(obj)
                if ot and ot != "Skeleton":
                    clothes = obj

        if not basemesh:
            self.report({'ERROR'}, "No basemesh selected")
            return {'CANCELLED'}

        if not clothes:
            self.report({'ERROR'}, "No clothes selected")
            return {'CANCELLED'}

        for modifier in clothes.modifiers:
            self.report({'ERROR'}, "Interpolating does not work when clothes have modifiers")
            return {'CANCELLED'}

        # The real clothes might match against helper mesh, but we want to hide the body mesh
        clothes_copy = clothes.copy()
        clothes_copy.data = clothes.data.copy()
        for group in clothes_copy.vertex_groups:
            clothes_copy.vertex_groups.remove(group)
        clothes_copy.vertex_groups.new(name="body")
        for vert in clothes_copy.data.vertices:
            clothes_copy.vertex_groups["body"].add([vert.index], 1.0, "REPLACE")

        mhclo = ClothesService.create_mhclo_from_clothes_matching(basemesh, clothes_copy)
        _LOG.debug("mhclo", mhclo)

        delete_group = MakeClothesObjectProperties.get_value("delete_group", entity_reference=clothes)

        if not delete_group:
            delete_group = "Delete"

        ClothesService.create_new_delete_group(basemesh, clothes_copy, mhclo, group_name=delete_group)

        ObjectService.delete_object(clothes_copy)

        self.report({'INFO'}, "A very rough delete group has been created on the basemesh. You should check and edit this manually before using it.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_GenDeleteOperator)
