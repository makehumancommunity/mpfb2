"""Operator for creating a new human object from presets."""

import bpy
from ....services import LogService
from ....services import LocationService
from ....services import HumanService
from ....services import ObjectService
from ....services import MeshService
from ....services import SystemService
from ...mpfboperator import MpfbOperator
from .... import ClassManager

_LOG = LogService.get_logger("newhuman.humanfrompresets")


class MPFB_OT_HumanFromPresetsOperator(MpfbOperator):
    """Create a new human from presets"""
    bl_idname = "mpfb.human_from_presets"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):

        _LOG.reset_timer()
        from ...newhuman.frompresetspanel import PRESETS_HUMAN_PROPERTIES  # pylint: disable=C0415

        name = PRESETS_HUMAN_PROPERTIES.get_value("available_presets", entity_reference=context.scene)

        if name is None or str(name).strip() == "":
            self.report({'ERROR'}, "Presets must be selected")
            return {'FINISHED'}

        deserialization_settings = HumanService.get_default_deserialization_settings()

        deserialization_settings["detailed_helpers"] = PRESETS_HUMAN_PROPERTIES.get_value("detailed_helpers", entity_reference=context.scene)
        deserialization_settings["extra_vertex_groups"] = PRESETS_HUMAN_PROPERTIES.get_value("extra_vertex_groups", entity_reference=context.scene)
        deserialization_settings["mask_helpers"] = PRESETS_HUMAN_PROPERTIES.get_value("mask_helpers", entity_reference=context.scene)
        deserialization_settings["load_clothes"] = PRESETS_HUMAN_PROPERTIES.get_value("load_clothes", entity_reference=context.scene)
        deserialization_settings["override_rig"] = PRESETS_HUMAN_PROPERTIES.get_value("override_rig", entity_reference=context.scene)
        deserialization_settings["override_skin_model"] = PRESETS_HUMAN_PROPERTIES.get_value("override_skin_model", entity_reference=context.scene)
        deserialization_settings["override_clothes_model"] = PRESETS_HUMAN_PROPERTIES.get_value("override_clothes_model", entity_reference=context.scene)
        deserialization_settings["override_eyes_model"] = PRESETS_HUMAN_PROPERTIES.get_value("override_eyes_model", entity_reference=context.scene)

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

        preselect_group = PRESETS_HUMAN_PROPERTIES.get_value("preselect_group", entity_reference=context.scene)
        if not preselect_group:
            preselect_group = None

        proxy = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Proxymeshes")
        if proxy:
            bpy.context.view_layer.objects.active = proxy
            proxy.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            MeshService.select_all_vertices_in_vertex_group_for_active_object(preselect_group, deselect_other=True)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            for slot in proxy.material_slots:
                if str(slot.material.name).lower().endswith(str(preselect_group).lower()):
                    proxy.active_material_index = slot.slot_index

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        MeshService.select_all_vertices_in_vertex_group_for_active_object(preselect_group, deselect_other=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for slot in basemesh.material_slots:
            if str(slot.material.name).lower().endswith(str(preselect_group).lower()):
                basemesh.active_material_index = slot.slot_index

        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, mpfb_type_name="Skeleton")
        if rig:
           bpy.context.view_layer.objects.active = rig
           basemesh.select_set(False)
           rig.select_set(True)

        _LOG.time("Human created in")

        self.report({'INFO'}, "Human created")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_HumanFromPresetsOperator)

