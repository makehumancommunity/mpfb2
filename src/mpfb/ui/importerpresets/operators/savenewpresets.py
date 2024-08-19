
from ....services import LogService
from ....services import UiService
from ....services import LocationService
from ...importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from mpfb._classmanager import ClassManager
import bpy, os

_LOG = LogService.get_logger("importeroperators.savenewpresets")


class MPFB_OT_SaveNewImporterPresetsOperator(bpy.types.Operator):
    """This will save new importer presets with a name from the text field above, using values from the fields below"""
    bl_idname = "mpfb.importerpresets_save_new_importer_presets"
    bl_label = "Save new importer presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()
        name = IMPORTER_PRESETS_PROPERTIES.get_value("name", entity_reference=context.scene)
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
