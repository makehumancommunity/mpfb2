"""Operator for loading the selected randomization preset into the panel."""

from .....services import LogService
from .....services import LocationService
from .....services import RandomizationService
from ..randomizeproperties import RANDOMIZE_PROPERTIES, spec_to_scene
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext, ContextResolveEffort
from ..... import ClassManager

_LOG = LogService.get_logger("ui.new_human.randomize.loadpreset")


class MPFB_OT_Randomize_Load_Preset_Operator(MpfbOperator):
    """This will load the randomization preset selected in the dropdown above, and use it to populate the settings below"""
    bl_idname = "mpfb.randomize_load_preset"
    bl_label = "Load selected preset"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        ctx = MpfbContext(context=context, scene_properties=RANDOMIZE_PROPERTIES, effort=ContextResolveEffort.NONE)

        if not ctx.available_presets:
            self.report({'ERROR'}, "No preset is selected")
            return {'FINISHED'}

        file_name = LocationService.get_user_config("randomization." + ctx.available_presets + ".json")
        spec = RandomizationService.deserialize_spec_from_json_file(file_name)
        spec_to_scene(spec, context.scene)
        self.report({'INFO'}, "Preset was loaded from " + file_name)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Randomize_Load_Preset_Operator)
