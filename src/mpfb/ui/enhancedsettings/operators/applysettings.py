#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.enhancedsettings.enhancedsettingspanel import ENHANCED_SETTINGS_PROPERTIES
from mpfb import CLASSMANAGER
import bpy, os, json

_LOG = LogService.get_logger("enhancedsettings.applysettings")


class MPFB_OT_ApplyEnhancedSettingsOperator(bpy.types.Operator):
    """This will load the enhanced material setting selected in the dropdown above, and use these to update the materials on the selected object"""
    bl_idname = "mpfb.enhancedsettings_apply_settings"
    bl_label = "Apply selected presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        name = ENHANCED_SETTINGS_PROPERTIES.get_value("available_settings", entity_reference=context)

        if not name:
            self.report({'ERROR'}, "Must select settings to load")
            return {'FINISHED'}

        file_name = LocationService.get_user_config("enhanced_settings." + name + ".json")

        if not os.path.exists(file_name):
            _LOG.error("Settings did not exist despite being in list:", file_name)
            self.report({'ERROR'}, "Settings did not exist!?")
            return {'FINISHED'}

        settings = dict()
        _LOG.debug("Will attempt to load", file_name)
        with open(file_name, "r") as json_file:
            settings = json.load(json_file)

        body = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Basemesh")
        if not body:
            body = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Proxymesh")

        if not body:
            self.report({'ERROR'}, "Could not find basemesh or body proxy amongst nearest relatives")
            return {'FINISHED'}

        if not MaterialService.has_materials(body):
            self.report({'ERROR'}, "Body does not have a material")
            return {'FINISHED'}

        _LOG.debug("material_slots", body.material_slots)

        for slot in body.material_slots:
            material = slot.material
            group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
            if group_node:
                values = NodeService.get_socket_default_values(group_node)
                if "colorMixIn" in values:
                    # This seems to be an enhanced skin material
                    name = material.name
                    if "." in name:
                        (prefix, name) = name.split(".", 2)
                    if "." in name:
                        (name, number) = name.split(".", 2)
                    _LOG.debug("final name", name)
                    if name in settings:
                        _LOG.debug("will try to apply settings", settings[name])
                        NodeService.set_socket_default_values(group_node, settings[name])

        self.report({'INFO'}, "Presets were loaded from " + file_name)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False
        name = ENHANCED_SETTINGS_PROPERTIES.get_value("available_settings", entity_reference=context)
        if not name:
            return False
        return True

CLASSMANAGER.add_class(MPFB_OT_ApplyEnhancedSettingsOperator)
