"""Operator for importing MHMAT weight."""

import bpy
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from mpfb import ClassManager

_LOG = LogService.get_logger("makeweight.importweights")

class MPFB_OT_ImportWeightsOperator(bpy.types.Operator, ImportHelper):
    """Import weights from json"""
    bl_idname = "mpfb.import_makeweight_weight"
    bl_label = "Import weights"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})

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

    def invoke(self, context, event):
        #blender_object = context.active_object
        #name = MakeWeightObjectProperties.get_value("name", entity_reference=blender_object)
        #self.filepath = bpy.path.clean_name(name, replace="-") + ".weight"
        return super().invoke(context, event)

    def execute(self, context):

        blender_object = context.active_object
        weight_string = Path(self.filepath).read_text()

        # TODO: parse json, assign weights...

        self.report({'INFO'}, "Weight file was imported")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ImportWeightsOperator)
