#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.ui.importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from mpfb import CLASSMANAGER
import bpy

_LOG = LogService.get_logger("importeroperators.overwritepresets")


class MPFB_OT_OverwriteImporterPresetsOperator(bpy.types.Operator):
    """This will overwrite the importer presets selected in the dropdown above, using values from the fields below"""
    bl_idname = "mpfb.importerpresets_overwrite_importer_presets"
    bl_label = "Overwrite selected presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()
        name = IMPORTER_PRESETS_PROPERTIES.get_value("available_presets", entity_reference=context.scene)
        file_name = LocationService.get_user_config("importer_presets." + name + ".json")
        excludes = ["available_presets", "name"]
        IMPORTER_PRESETS_PROPERTIES.serialize_to_json(file_name, entity_reference=context.scene, exclude_keys=excludes)
        self.report({'INFO'}, "Presets were written to " + file_name)
        return {'FINISHED'}


CLASSMANAGER.add_class(MPFB_OT_OverwriteImporterPresetsOperator)
