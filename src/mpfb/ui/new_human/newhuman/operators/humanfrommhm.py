"""Operator for creating a new human object from presets."""

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from .....services import LogService
from .....services import HumanService
from .....services import ObjectService
from .....services import SystemService
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext
from ..... import ClassManager

_LOG = LogService.get_logger("newhuman.humanfrommhm")

class MPFB_OT_HumanFromMHMOperator(MpfbOperator, ImportHelper):
    """Create a new human from MHM"""
    bl_idname = "mpfb.human_from_mhm"
    bl_label = "Import MHM"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.mhm', options={'HIDDEN'})

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):

        _LOG.reset_timer()

        from ...newhuman.frompresetspanel import PRESETS_HUMAN_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=PRESETS_HUMAN_PROPERTIES)

        _LOG.debug("filepath", self.filepath)

        deserialization_settings = HumanService.get_default_deserialization_settings()

        ctx.populate_dict(deserialization_settings, [
            "detailed_helpers", "extra_vertex_groups", "mask_helpers",
            "load_clothes", "override_rig", "override_skin_model",
            "bodypart_deep_search", "clothes_deep_search",
            "override_clothes_model", "override_eyes_model"
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

