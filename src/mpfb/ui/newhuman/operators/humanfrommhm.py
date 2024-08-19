"""Operator for creating a new human object from presets."""

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from ....services import LogService
from ....services import HumanService
from ....services import ObjectService
from ....services import SystemService
from mpfb.ui.mpfboperator import MpfbOperator
from mpfb import ClassManager

_LOG = LogService.get_logger("newhuman.humanfrommhm")


class MPFB_OT_HumanFromMHMOperator(MpfbOperator, ImportHelper):
    """Create a new human from MHM"""
    bl_idname = "mpfb.human_from_mhm"
    bl_label = "Import MHM"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.mhm', options={'HIDDEN'})

    def __init__(self):
        MpfbOperator.__init__(self, "newhuman.humanfrommhm")

    def hardened_execute(self, context):

        _LOG.reset_timer()

        from mpfb.ui.newhuman.frompresetspanel import PRESETS_HUMAN_PROPERTIES  # pylint: disable=C0415

        _LOG.debug("filepath", self.filepath)

        deserialization_settings = HumanService.get_default_deserialization_settings()

        deserialization_settings["detailed_helpers"] = PRESETS_HUMAN_PROPERTIES.get_value("detailed_helpers", entity_reference=context.scene)
        deserialization_settings["extra_vertex_groups"] = PRESETS_HUMAN_PROPERTIES.get_value("extra_vertex_groups", entity_reference=context.scene)
        deserialization_settings["mask_helpers"] = PRESETS_HUMAN_PROPERTIES.get_value("mask_helpers", entity_reference=context.scene)
        deserialization_settings["load_clothes"] = PRESETS_HUMAN_PROPERTIES.get_value("load_clothes", entity_reference=context.scene)
        deserialization_settings["override_rig"] = PRESETS_HUMAN_PROPERTIES.get_value("override_rig", entity_reference=context.scene)
        deserialization_settings["override_skin_model"] = PRESETS_HUMAN_PROPERTIES.get_value("override_skin_model", entity_reference=context.scene)
        deserialization_settings["bodypart_deep_search"] = PRESETS_HUMAN_PROPERTIES.get_value("bodypart_deep_search", entity_reference=context.scene)
        deserialization_settings["clothes_deep_search"] = PRESETS_HUMAN_PROPERTIES.get_value("clothes_deep_search", entity_reference=context.scene)
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

        basemesh = HumanService.deserialize_from_mhm(self.filepath, deserialization_settings)

        _LOG.debug("Basemesh", basemesh)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, mpfb_type_name="Skeleton")
        if rig:
            bpy.context.view_layer.objects.active = rig
            basemesh.select_set(False)
            rig.select_set(True)

        HumanService.refit(basemesh)

        _LOG.time("Human created in")

        # from mpfb.entities.primitiveprofiler import PrimitiveProfiler
        # human_profiler = PrimitiveProfiler("HumanService")
        # target_profiler = PrimitiveProfiler("TargetService")
        # human_profiler.dump()
        # target_profiler.dump()

        self.report({'INFO'}, "Human created. You should check the model, as the MHM might not map exactly to what is available in MPFB2.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_HumanFromMHMOperator)

