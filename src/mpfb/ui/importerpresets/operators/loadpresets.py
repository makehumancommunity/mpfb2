#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.ui.importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("importeroperators.loadpresets")


class MPFB_OT_LoadImporterPresetsOperator(bpy.types.Operator):
    """This will load the importer presets selected in the dropdown above, and use these presets to populate the fields below"""
    bl_idname = "mpfb.importerpresets_load_importer_presets"
    bl_label = "Load selected presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()
        name = IMPORTER_PRESETS_PROPERTIES.get_value("available_presets", entity_reference=context.scene)
        file_name = LocationService.get_user_config("importer_presets." + name + ".json")
        IMPORTER_PRESETS_PROPERTIES.deserialize_from_json(file_name, entity_reference=context.scene)
        self.report({'INFO'}, "Presets were loaded from " + file_name)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_LoadImporterPresetsOperator)
