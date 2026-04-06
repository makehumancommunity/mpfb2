from .....services import LogService
from .....services import UiService
from .....services import LocationService
from .....services import ObjectService
from .....services import NodeService
from .....services import MaterialService
from .....services import HumanService
from .....services import RigService
from ...humanpresets.humanpresetspanel import HUMAN_PRESETS_PROPERTIES
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
import bpy, os, json

_LOG = LogService.get_logger("humanpresets.savenewpresets")


@pollstrategy(PollStrategy.BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE)
class MPFB_OT_Save_New_Presets_Operator(MpfbOperator):
    """This will save new human preset"""
    bl_idname = "mpfb.save_new_human_presets"
    bl_label = "Save new presets"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        if context.active_object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        from .....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=HUMAN_PRESETS_PROPERTIES)
        name = ctx.name
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "A valid name must be given")
            return {'FINISHED'}
        if " " in str(name):
            self.report({'ERROR'}, "Human presets names should not contain spaces")
            return {'FINISHED'}

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "human." + name + ".json")
        if os.path.exists(file_name):
            self.report({'ERROR'}, "Presets with that name already exist")
            return {'FINISHED'}

        basemesh = None
        if ObjectService.object_is_basemesh(context.active_object):
            basemesh = context.active_object
        else:
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")

        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'FINISHED'}

        HumanService.serialize_to_json_file(basemesh, file_name, True)

        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        if rig and "generated" in RigService.identify_rig(rig):
            self.report({'WARNING'}, "Serializing a generated rig might cause issues. The preset was saved, but you should load it and see if it is correct.")
        else:
            self.report({'INFO'}, "Human saved as " + file_name)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_New_Presets_Operator)
