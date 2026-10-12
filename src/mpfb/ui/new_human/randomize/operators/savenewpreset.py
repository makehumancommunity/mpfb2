"""Operator for saving a new randomization preset."""

import os
from .....services import LogService
from .....services import LocationService
from .....services import RandomizationService
from ..randomizeproperties import RANDOMIZE_PROPERTIES, scene_to_spec, rebuild_preset_list
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext, ContextResolveEffort
from ..... import ClassManager

_LOG = LogService.get_logger("ui.new_human.randomize.savenewpreset")


class MPFB_OT_Randomize_Save_New_Preset_Operator(MpfbOperator):
    """This will save a new randomization preset with the name from the text field above, using the settings below"""
    bl_idname = "mpfb.randomize_save_new_preset"
    bl_label = "Save new preset"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        ctx = MpfbContext(context=context, scene_properties=RANDOMIZE_PROPERTIES, effort=ContextResolveEffort.NONE)

        name = ctx.name
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "A valid name must be given")
            return {'FINISHED'}
        if " " in str(name):
            self.report({'ERROR'}, "Preset names should not contain spaces")
            return {'FINISHED'}

        file_name = LocationService.get_user_config("randomization." + name + ".json")
        if os.path.exists(file_name):
            self.report({'ERROR'}, "A preset with that name already exists")
            return {'FINISHED'}

        RandomizationService.serialize_spec_to_json_file(scene_to_spec(context.scene), file_name)
        rebuild_preset_list()
        self.report({'INFO'}, "Preset was written to " + file_name)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Randomize_Save_New_Preset_Operator)
