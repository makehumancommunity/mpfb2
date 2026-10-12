"""Operator for overwriting the selected randomization preset."""

from .....services import LogService
from .....services import LocationService
from .....services import RandomizationService
from ..randomizeproperties import RANDOMIZE_PROPERTIES, scene_to_spec
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext, ContextResolveEffort
from ..... import ClassManager

_LOG = LogService.get_logger("ui.new_human.randomize.overwritepreset")


class MPFB_OT_Randomize_Overwrite_Preset_Operator(MpfbOperator):
    """This will overwrite the randomization preset selected in the dropdown above, using the settings below"""
    bl_idname = "mpfb.randomize_overwrite_preset"
    bl_label = "Overwrite selected preset"
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
        RandomizationService.serialize_spec_to_json_file(scene_to_spec(context.scene), file_name)
        self.report({'INFO'}, "Preset was written to " + file_name)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Randomize_Overwrite_Preset_Operator)
