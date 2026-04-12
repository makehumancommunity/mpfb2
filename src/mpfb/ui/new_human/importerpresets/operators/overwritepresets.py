
from .....services import LogService
from .....services import LocationService
from ...importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext, ContextResolveEffort
import bpy

_LOG = LogService.get_logger("importeroperators.overwritepresets")

class MPFB_OT_OverwriteImporterPresetsOperator(MpfbOperator):
    """This will overwrite the importer presets selected in the dropdown above, using values from the fields below"""
    bl_idname = "mpfb.importerpresets_overwrite_importer_presets"
    bl_label = "Overwrite selected presets"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        ctx = MpfbContext(context=context, scene_properties=IMPORTER_PRESETS_PROPERTIES, effort=ContextResolveEffort.NONE)

        file_name = LocationService.get_user_config("importer_presets." + ctx.available_presets + ".json")
        excludes = ["available_presets", "name"]
        IMPORTER_PRESETS_PROPERTIES.serialize_to_json(file_name, entity_reference=context.scene, exclude_keys=excludes)
        self.report({'INFO'}, "Presets were written to " + file_name)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_OverwriteImporterPresetsOperator)
