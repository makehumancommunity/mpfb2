
from ....services import LogService
from ....services import UiService
from ....services import LocationService
from ...importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from .... import ClassManager
from ...mpfboperator import MpfbOperator
import bpy, os

_LOG = LogService.get_logger("importeroperators.savenewpresets")


class MPFB_OT_SaveNewImporterPresetsOperator(MpfbOperator):
    """This will save new importer presets with a name from the text field above, using values from the fields below"""
    bl_idname = "mpfb.importerpresets_save_new_importer_presets"
    bl_label = "Save new importer presets"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        from ...mpfbcontext import MpfbContext, ContextResolveEffort  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=IMPORTER_PRESETS_PROPERTIES, effort=ContextResolveEffort.NONE)

        name = ctx.name
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "A valid name must be given")
            return {'FINISHED'}
        if " " in str(name):
            self.report({'ERROR'}, "Presets names should not contain spaces")
            return {'FINISHED'}

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "importer_presets." + name + ".json")
        if os.path.exists(file_name):
            self.report({'ERROR'}, "Presets with that name already exist")
            return {'FINISHED'}

        excludes = ["available_presets", "name"]
        IMPORTER_PRESETS_PROPERTIES.serialize_to_json(file_name, entity_reference=context.scene, exclude_keys=excludes)

        UiService.rebuild_importer_presets_panel_list()
        UiService.rebuild_importer_panel_list()
        self.report({'INFO'}, "Presets were written to " + file_name)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_SaveNewImporterPresetsOperator)
