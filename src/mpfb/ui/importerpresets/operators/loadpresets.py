
from ....services import LogService
from ....services import LocationService
from ...importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from .... import ClassManager
from ...mpfboperator import MpfbOperator
import bpy

_LOG = LogService.get_logger("importeroperators.loadpresets")


class MPFB_OT_LoadImporterPresetsOperator(MpfbOperator):
    """This will load the importer presets selected in the dropdown above, and use these presets to populate the fields below"""
    bl_idname = "mpfb.importerpresets_load_importer_presets"
    bl_label = "Load selected presets"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        from ...mpfbcontext import MpfbContext, ContextResolveEffort  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=IMPORTER_PRESETS_PROPERTIES, effort=ContextResolveEffort.NONE)

        file_name = LocationService.get_user_config("importer_presets." + ctx.available_presets + ".json")
        IMPORTER_PRESETS_PROPERTIES.deserialize_from_json(file_name, entity_reference=context.scene)
        self.report({'INFO'}, "Presets were loaded from " + file_name)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_LoadImporterPresetsOperator)
