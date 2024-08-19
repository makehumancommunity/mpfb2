"""Operator for checking a clothes object."""

import bpy, os
from ....services import LogService
from ....services import LocationService
from ....services import ObjectService
from ....services import ClothesService
from ....services import MaterialService
from ...makeclothes import MakeClothesObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from ...makeclothes.operators.clothescommon import ClothesCommon
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.checkclothes")

CLOTHES_CHECKS = dict()


class MPFB_OT_CheckClothesOperator(bpy.types.Operator):
    """Perform basic sanity checks on the active object. You need to click this again if changing the clothes, the panel will not update automatically. Note that this operation might a long time depending on the number of vertex groups and the number of vertices"""
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

        CLOTHES_CHECKS[uuid_value] = ClothesService.mesh_is_valid_as_clothes(clothes, basemesh)
        self.report({'INFO'}, "Clothes check performed, see panel")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CheckClothesOperator)
