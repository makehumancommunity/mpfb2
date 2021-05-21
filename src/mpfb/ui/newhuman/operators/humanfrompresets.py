"""Operator for creating a new human object from presets."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.humanservice import HumanService
from mpfb import ClassManager

_LOG = LogService.get_logger("newhuman.humanfrompresets")
_LOG.set_level(LogService.DUMP)

class MPFB_OT_HumanFromPresetsOperator(bpy.types.Operator):
    """Create a new human from presets"""
    bl_idname = "mpfb.human_from_presets"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        from mpfb.ui.newhuman.frompresetspanel import PRESETS_HUMAN_PROPERTIES  # pylint: disable=C0415

        name = PRESETS_HUMAN_PROPERTIES.get_value("available_presets", entity_reference=context.scene)

        if name is None or str(name).strip() == "":
            self.report({'ERROR'}, "Presets must be selected")
            return {'FINISHED'}

        detailed_helpers = PRESETS_HUMAN_PROPERTIES.get_value("detailed_helpers", entity_reference=context.scene)
        extra_vertex_groups = PRESETS_HUMAN_PROPERTIES.get_value("extra_vertex_groups", entity_reference=context.scene)
        mask_helpers = PRESETS_HUMAN_PROPERTIES.get_value("mask_helpers", entity_reference=context.scene)
        scale_factor = PRESETS_HUMAN_PROPERTIES.get_value("scale_factor", entity_reference=context.scene)

        scale = 0.1

        if scale_factor == "DECIMETER":
            scale = 1.0

        if scale_factor == "CENTIMETER":
            scale = 10.0

        fullname = "human." + name + ".json"
        filename = LocationService.get_user_config(fullname)

        _LOG.debug("filename", filename)

        basemesh = HumanService.deserialize_from_json_file(filename,
                                                           mask_helpers=mask_helpers,
                                                           detailed_helpers=detailed_helpers,
                                                           extra_vertex_groups=extra_vertex_groups,
                                                           feet_on_ground=True,
                                                           scale=scale)

        _LOG.debug("Basemesh", basemesh)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_HumanFromPresetsOperator)

