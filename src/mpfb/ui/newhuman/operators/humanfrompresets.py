"""Operator for creating a new human object from presets."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.humanservice import HumanService
from mpfb.services.objectservice import ObjectService
from mpfb.services.systemservice import SystemService
from mpfb import ClassManager

_LOG = LogService.get_logger("newhuman.humanfrompresets")

class MPFB_OT_HumanFromPresetsOperator(bpy.types.Operator):
    """Create a new human from presets"""
    bl_idname = "mpfb.human_from_presets"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        if not SystemService.check_for_obj_importer():
            self.report({'ERROR'}, "The \"Import-Export Wavefront OBJ format\" addon seems to be disabled. You need to enable this in the preferences.")
            return {'FINISHED'}

        _LOG.reset_timer()
        from mpfb.ui.newhuman.frompresetspanel import PRESETS_HUMAN_PROPERTIES  # pylint: disable=C0415

        name = PRESETS_HUMAN_PROPERTIES.get_value("available_presets", entity_reference=context.scene)

        if name is None or str(name).strip() == "":
            self.report({'ERROR'}, "Presets must be selected")
            return {'FINISHED'}

        deserialization_settings = HumanService.get_default_deserialization_settings()

        deserialization_settings["detailed_helpers"] = PRESETS_HUMAN_PROPERTIES.get_value("detailed_helpers", entity_reference=context.scene)
        deserialization_settings["extra_vertex_groups"] = PRESETS_HUMAN_PROPERTIES.get_value("extra_vertex_groups", entity_reference=context.scene)
        deserialization_settings["mask_helpers"] = PRESETS_HUMAN_PROPERTIES.get_value("mask_helpers", entity_reference=context.scene)
        deserialization_settings["load_clothes"] = PRESETS_HUMAN_PROPERTIES.get_value("load_clothes", entity_reference=context.scene)

        scale_factor = PRESETS_HUMAN_PROPERTIES.get_value("scale_factor", entity_reference=context.scene)
        scale = 0.1

        if scale_factor == "DECIMETER":
            scale = 1.0

        if scale_factor == "CENTIMETER":
            scale = 10.0

        deserialization_settings["scale"] = scale

        _LOG.debug("Deserialization settings", deserialization_settings)

        fullname = "human." + name + ".json"
        filename = LocationService.get_user_config(fullname)

        _LOG.debug("filename", filename)

        basemesh = HumanService.deserialize_from_json_file(filename, deserialization_settings)

        _LOG.debug("Basemesh", basemesh)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, mpfb_type_name="Skeleton")
        if rig:
            bpy.context.view_layer.objects.active = rig
            basemesh.select_set(False)
            rig.select_set(True)

        _LOG.time("Human created in")

        self.report({'INFO'}, "Human created")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_HumanFromPresetsOperator)

