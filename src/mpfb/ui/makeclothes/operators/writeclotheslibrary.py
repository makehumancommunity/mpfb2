"""Operator for saving a MHCLO file."""

import bpy, os, re
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import LocationService
from ....services import ObjectService
from ....services import ClothesService
from ....services import AssetService
from ...makeclothes import MakeClothesObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from ...makeclothes.operators.clothescommon import ClothesCommon
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.writeclotheslibrary")

class MPFB_OT_WriteClothesLibraryOperator(bpy.types.Operator, ClothesCommon):
    """Export the asset to the relevant section in the asset library. The file name will be based on the 'name' text box"""
    bl_idname = "mpfb.write_makeclothes_library"
    bl_label = "Store in library"
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


        name = MakeClothesObjectProperties.get_value("name", entity_reference=clothes)
        if not name or not str(name).strip():
            self.report({'ERROR'}, "No asset name specified")
            return {'CANCELLED'}

        obj_type = GeneralObjectProperties.get_value("object_type", entity_reference=clothes)
        if not obj_type or not str(obj_type).strip():
            self.report({'ERROR'}, "No object type set for this asset")
            return {'CANCELLED'}

        root = LocationService.get_user_data(str(obj_type).lower())
        cleaned_name = str(name).strip().replace(" ", "_")
        cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '_', cleaned_name)
        cleaned_name = re.sub(r'_+', '_', cleaned_name)

        asset_dir = os.path.join(root, cleaned_name)
        if not os.path.exists(asset_dir):
            os.makedirs(asset_dir)

        file_name = bpy.path.abspath(os.path.join(asset_dir, cleaned_name + ".mhclo"))

        result = self.generic_execute(context, file_name)
        if result != {'FINISHED'}:
            return result

        AssetService.update_all_asset_lists()

        return result


ClassManager.add_class(MPFB_OT_WriteClothesLibraryOperator)
