"""Operator for checking a clothes object."""

import bpy, os
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.clothesservice import ClothesService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.makeclothes import MakeClothesObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.ui.makeclothes.operators.clothescommon import ClothesCommon
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.checkclothes")

CLOTHES_CHECKS = dict()


class MPFB_OT_CheckClothesOperator(bpy.types.Operator):
    """Perform basic sanity checks on the active object. You need to click this again if changing the clothes, the panel will not update automatically"""
    bl_idname = "mpfb.check_makeclothes_clothes"
    bl_label = "Check"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

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

        uuid_value = GeneralObjectProperties.get_value("uuid", entity_reference=clothes)
        if not uuid_value:
            self.report({'ERROR'}, "No UUID found for the selected clothes")
            return {'CANCELLED'}

        CLOTHES_CHECKS[uuid_value] = ClothesService.mesh_is_valid_as_clothes(clothes)
        self.report({'INFO'}, "Clothes check performed, see panel")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CheckClothesOperator)
