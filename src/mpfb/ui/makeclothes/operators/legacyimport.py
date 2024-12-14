"""Operator for importing properties set by the legacy MakeClothes addon."""

from ....services import LogService
from ....services import ObjectService
from ....entities.objectproperties import GeneralObjectProperties
from .. import MakeClothesObjectProperties
from .... import ClassManager
from ...mpfboperator import MpfbOperator

_LOG = LogService.get_logger("makeclothes.legacyimport")

_LEGACY_CLOTHES_OBJ_PROPS = {
    "MhClothesDesc": "description",
    "MhClothesName": "name",
    "MhDeleteGroup": "delete_group",
    }

_LEGACY_CLOTHES_SCENE_PROPS = {
    "MhClothesLicense": "license",
    "MhClothesAuthor": "author"
    }

class MPFB_OT_LegacyImportOperator(MpfbOperator):
    """Attempt to import properties set by legacy MakeClothes"""
    bl_idname = "mpfb.legacy_makeclothes_import"
    bl_label = "Import legacy props"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return context.active_object.type == "MESH"
        return False

    def hardened_execute(self, context):
        """Import properties from legacy MakeClothes"""
        blender_object = context.active_object
        scene = context.scene

        GeneralObjectProperties.set_value("scale_factor", 1.0, entity_reference=blender_object)

        if not ObjectService.object_is_basemesh(blender_object):

            for key_name in _LEGACY_CLOTHES_OBJ_PROPS:
                if hasattr(blender_object, key_name):
                    legacy_value = getattr(blender_object, key_name)
                    new_key = _LEGACY_CLOTHES_OBJ_PROPS[key_name]
                    MakeClothesObjectProperties.set_value(new_key, legacy_value, entity_reference=blender_object)
                else:
                    _LOG.debug("Object property not found on object", key_name)

            for key_name in _LEGACY_CLOTHES_SCENE_PROPS:
                if hasattr(scene, key_name):
                    legacy_value = getattr(scene, key_name)
                    new_key = _LEGACY_CLOTHES_SCENE_PROPS[key_name]
                    MakeClothesObjectProperties.set_value(new_key, legacy_value, entity_reference=blender_object)
                else:
                    _LOG.debug("Scene property not found", key_name)

        self.report({'INFO'}, "Properties were imported")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_LegacyImportOperator)
