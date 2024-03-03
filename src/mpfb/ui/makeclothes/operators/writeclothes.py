"""Operator for saving a MHCLO file."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.clothesservice import ClothesService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.makeclothes import MakeClothesObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.writeclothes")

class MPFB_OT_WriteClothesOperator(bpy.types.Operator, ExportHelper):
    """Export the asset to MHCLO + MHMAT + obj, with filenames based on the mhclo file. Use this if you don't want to store the asset in your local asset library"""
    bl_idname = "mpfb.write_makeclothes_clothes"
    bl_label = "Save as files"
    bl_options = {'REGISTER'}

    filename_ext = '.mhclo'

    filter_glob: StringProperty(default='*.mhclo')
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        # TODO: support blender materials
        #=======================================================================
        # if not self.filepath:
        #     blend_filepath = context.active_object.MhMsName
        #     # just in case ... ;)
        #     if not blend_filepath:
        #         blend_filepath = "untitled"
        #     self.filepath = blend_filepath + self.filename_ext
        #=======================================================================

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):

        if not self.filepath:
            self.report({'ERROR'}, "No file path specified")
            return {'CANCELLED'}

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

        _LOG.debug("basemesh, clothes", (basemesh, clothes))

        check = ClothesService.mesh_is_valid_as_clothes(clothes)
        if not check["all_checks_ok"]:
            _LOG.error("Clothes check failed", check)
            self.report({'ERROR'}, "The selected object is not valid as clothes")
            return {'CANCELLED'}

        cache_dir = LocationService.get_user_cache("basemesh_xref")
        if not os.path.exists(cache_dir):
            self.report({'ERROR'}, "No basemesh xref cache available")
            return {'CANCELLED'}

        props_dict = {}
        for prop in ["author", "description", "name", "homepage", "license"]:
            props_dict[prop] = MakeClothesObjectProperties.get_value(prop, entity_reference=clothes)
        for prop in ["uuid"]:
            props_dict[prop] = GeneralObjectProperties.get_value(prop, entity_reference=clothes)

        mhclo = ClothesService.create_mhclo_from_clothes_matching(basemesh, clothes, properties_dict=props_dict)
        _LOG.debug("mhclo", mhclo)

        file_name = bpy.path.abspath(self.filepath)
        matbn = None

        from mpfb.ui.makeclothes.makeclothespanel import MAKECLOTHES_PROPERTIES
        save_material = MAKECLOTHES_PROPERTIES.get_value("save_material", entity_reference=context.scene)

        mat_type = None
        if MaterialService.has_materials(clothes):
            obj_mat = MaterialService.get_material(clothes)
            mat_type = MaterialService.identify_material(obj_mat)

        if save_material and mat_type == "makeskin":
            material = MakeSkinMaterial()
            material.populate_from_object(clothes)

            dirn = os.path.dirname(file_name)
            bn = os.path.basename(file_name).replace(".mhclo", "")
            matbn = bn + ".mhmat"
            matn = os.path.join(dirn, matbn)

            _LOG.debug("Material file name", matn)

            image_file_error = material.check_that_all_textures_are_saved(clothes, dirn, bn)
            if image_file_error is not None:
                self.report({'ERROR'}, image_file_error)
                return {'FINISHED'}

            material.export_to_disk(matn)

        mhclo.material = matbn

        file_name = os.path.abspath(file_name)
        if not str(file_name).endswith(".mhclo") and os.path.exists(file_name):
            self.report({'ERROR'}, "Refusing to overwrite existing file without mhclo extension")
            return {'CANCELLED'}

        reference_scale = ClothesService.get_reference_scale(basemesh) # TODO: ability to specify body part
        _LOG.debug("reference_scale", reference_scale)
        mhclo.write_mhclo(file_name, reference_scale=reference_scale, also_export_mhmat=(matbn != None))

        self.report({'INFO'}, "The MHCLO file was written as " + file_name)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteClothesOperator)
