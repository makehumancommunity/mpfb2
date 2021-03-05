"""Operator for loading and applying eye material settings."""

from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.eyesettings.eyesettingspanel import EYE_SETTINGS_PROPERTIES
from mpfb._classmanager import ClassManager
import bpy, os, json

_LOG = LogService.get_logger("eyesettings.applysettings")


class MPFB_OT_ApplyEyeSettingsOperator(bpy.types.Operator):
    """This will load the eye material setting selected in the dropdown above, and use these to update the materials on the selected object"""
    bl_idname = "mpfb.eyesettings_apply_settings"
    bl_label = "Apply selected presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        name = EYE_SETTINGS_PROPERTIES.get_value("available_settings", entity_reference=context)

        if not name:
            self.report({'ERROR'}, "Must select settings to load")
            return {'FINISHED'}

        file_name = LocationService.get_user_config("eye_settings." + name + ".json")

        if not os.path.exists(file_name):
            _LOG.error("Settings did not exist despite being in list:", file_name)
            self.report({'ERROR'}, "Settings did not exist!?")
            return {'FINISHED'}

        settings = dict()
        _LOG.debug("Will attempt to load", file_name)
        with open(file_name, "r") as json_file:
            settings = json.load(json_file)

        eyes = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Eyes")

        if not eyes:
            self.report({'ERROR'}, "Could not find eyes amongst nearest relatives")
            return {'FINISHED'}

        if not MaterialService.has_materials(eyes):
            self.report({'ERROR'}, "Eyes do not have a material")
            return {'FINISHED'}

        _LOG.debug("material_slots", eyes.material_slots)

        slot = eyes.material_slots[0]

        material = slot.material
        group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
        if group_node:
            material_settings = NodeService.get_socket_default_values(group_node)
            if "IrisMinorColor" in material_settings:
                _LOG.debug("will try to apply settings", settings)
                NodeService.set_socket_default_values(group_node, settings)
            else:
                self.report({'ERROR'}, "Eyes do not seem to have procedural eyes material")
                return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Eyes do not seem to have procedural eyes material")
            return {'FINISHED'}

        self.report({'INFO'}, "Settings were loaded from " + file_name)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False
        name = EYE_SETTINGS_PROPERTIES.get_value("available_settings", entity_reference=context)
        if not name:
            return False
        return True

ClassManager.add_class(MPFB_OT_ApplyEyeSettingsOperator)
