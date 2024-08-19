"""Mode independent functionality for saving a MHCLO file."""

import bpy, os
from ....services import LogService
from ....services import LocationService
from ....services import ObjectService
from ....services import ClothesService
from ....services import MaterialService
from ...makeclothes import MakeClothesObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.clothescommon")


class ClothesCommon():

    def generic_execute(self, context, file_name):

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

        check = ClothesService.mesh_is_valid_as_clothes(clothes, basemesh)
        if not check["all_checks_ok"]:
            _LOG.error("Clothes check failed", check)
            self.report({'ERROR'}, "The selected object is not valid as clothes. Perform clothes check?")
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

        delete_group = MakeClothesObjectProperties.get_value("delete_group", entity_reference=clothes)

        mhclo = None
        try:
            mhclo = ClothesService.create_mhclo_from_clothes_matching(basemesh, clothes, properties_dict=props_dict, delete_group=delete_group)
            _LOG.debug("mhclo", mhclo)
        except ValueError as e:
            _LOG.error("Error creating MHCLO", e)
            _LOG.error("Clothes check object", check)
            self.report({'ERROR'}, "Error creating MHCLO. Do a clothes check and/or check the log for details.")
            return {'CANCELLED'}

        matbn = None

        from ...makeclothes.makeclothespanel import MAKECLOTHES_PROPERTIES
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

        reference_scale = ClothesService.get_reference_scale(basemesh)  # TODO: ability to specify body part
        _LOG.debug("reference_scale", reference_scale)
        mhclo.write_mhclo(file_name, reference_scale=reference_scale, also_export_mhmat=(matbn != None))

        self.report({'INFO'}, "The MHCLO file was written as " + file_name)
        return {'FINISHED'}
