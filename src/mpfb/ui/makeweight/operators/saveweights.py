"""Operator for writing a MHMAT file."""

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb import ClassManager

_LOG = LogService.get_logger("makeweight.writeweights")

class MPFB_OT_SaveWeightsOperator(bpy.types.Operator, ExportHelper):
    """Save weights to weight file"""
    bl_idname = "mpfb.save_makeweight_weight"
    bl_label = "Save weights"
    bl_options = {'REGISTER'}

    filename_ext = '.json'

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if ObjectService.object_is_basemesh(context.active_object):
            return True
        if ObjectService.object_is_skeleton(context.active_object):
            return True
        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        if rig:
            return True
        return False

    def execute(self, context):
        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature_object, mpfb_type_name="Basemesh")

        if basemesh is None:
            self.report({'ERROR'}, "Could not find related basemesh. It should have been parent or child of armature object.")
            return {'FINISHED'}

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        weights = RigService.get_weights(armature_object, basemesh)

        with open(absolute_file_path, "w") as json_file:
            json.dump(weights, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)


ClassManager.add_class(MPFB_OT_SaveWeightsOperator)
