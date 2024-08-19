from ....services import LogService
from ....services import LocationService
from ....services import ObjectService
from ....services import HumanService
from ....services import RigService
from mpfb.ui.humanpresets.humanpresetspanel import HUMAN_PRESETS_PROPERTIES
from mpfb._classmanager import ClassManager
import bpy, os

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

        basemesh = None
        if ObjectService.object_is_basemesh(context.object):
            basemesh = context.object
        else:
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Basemesh")

        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'FINISHED'}

        HumanService.serialize_to_json_file(basemesh, file_name, True)

        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Skeleton")
        if rig and "generated" in RigService.identify_rig(rig):
            self.report({'WARNING'}, "Serializing a generated rig might cause issues. The preset was saved, but you should load it and see if it is correct.")
        else:
            self.report({'INFO'}, "Human saved as " + file_name)

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
