from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.services.materialservice import MaterialService
from mpfb.services.humanservice import HumanService
from mpfb.services.rigservice import RigService
from mpfb.ui.humanpresets.humanpresetspanel import HUMAN_PRESETS_PROPERTIES
from mpfb._classmanager import ClassManager
import bpy, os, json

_LOG = LogService.get_logger("humanpresets.savenewpresets")


class MPFB_OT_Save_New_Presets_Operator(bpy.types.Operator):
    """This will save new human preset"""
    bl_idname = "mpfb.save_new_human_presets"
    bl_label = "Save new presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        name = HUMAN_PRESETS_PROPERTIES.get_value("name", entity_reference=context)
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


ClassManager.add_class(MPFB_OT_Save_New_Presets_Operator)
