from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.services.humanservice import HumanService
from mpfb.ui.humanpresets.humanpresetspanel import HUMAN_PRESETS_PROPERTIES
from mpfb._classmanager import ClassManager
import bpy, os, json

_LOG = LogService.get_logger("humanpresets.overwritepresets")


class MPFB_OT_Overwrite_Human_Presets_Operator(bpy.types.Operator):
    """This will overwrite the selected human presets, using values from the selected object"""
    bl_idname = "mpfb.overwrite_human_presets"
    bl_label = "Overwrite presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        name = HUMAN_PRESETS_PROPERTIES.get_value("available_presets", entity_reference=context)
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "Presets must be chosen from the list")
            return {'FINISHED'}

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "human." + name + ".json")

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            return False

        if ObjectService.object_is_basemesh_or_body_proxy(obj):
            return True

        if ObjectService.object_is_skeleton(obj):
            return True

        return False

ClassManager.add_class(MPFB_OT_Overwrite_Human_Presets_Operator)
