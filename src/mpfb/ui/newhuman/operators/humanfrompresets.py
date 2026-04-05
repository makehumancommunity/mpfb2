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
        from ...mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=PRESETS_HUMAN_PROPERTIES)

        if ctx.available_presets is None or str(ctx.available_presets).strip() == "":
            self.report({'ERROR'}, "Presets must be selected")
            return {'FINISHED'}

        deserialization_settings = HumanService.get_default_deserialization_settings()

        ctx.populate_dict(deserialization_settings, [
            "detailed_helpers", "extra_vertex_groups", "mask_helpers",
            "load_clothes", "override_rig", "override_skin_model",
            "override_clothes_model", "override_eyes_model", "material_instances"
        ])

        if "rigify" in deserialization_settings["override_rig"] and not SystemService.check_for_rigify():
            self.report({'ERROR'}, "Rig override set to rigify, but rigify is not enabled.")
            return {'FINISHED'}

        scale = 0.1

        if ctx.scale_factor == "DECIMETER":
            scale = 1.0

        if ctx.scale_factor == "CENTIMETER":
            scale = 10.0

        deserialization_settings["scale"] = scale

        _LOG.debug("Deserialization settings", deserialization_settings)

        fullname = "human." + ctx.available_presets + ".json"
        filename = LocationService.get_user_config(fullname)

        _LOG.debug("filename", filename)

        basemesh = HumanService.deserialize_from_json_file(filename, deserialization_settings)

        _LOG.debug("Basemesh", basemesh)

        proxy = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Proxymeshes")
        if proxy:
            bpy.context.view_layer.objects.active = proxy
            proxy.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            MeshService.select_all_vertices_in_vertex_group_for_active_object(ctx.preselect_group or None, deselect_other=True)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            for slot in proxy.material_slots:
                if str(slot.material.name).lower().endswith(str(ctx.preselect_group).lower()):
                    proxy.active_material_index = slot.slot_index

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        MeshService.select_all_vertices_in_vertex_group_for_active_object(ctx.preselect_group or None, deselect_other=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for slot in basemesh.material_slots:
            if str(slot.material.name).lower().endswith(str(ctx.preselect_group).lower()):
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

