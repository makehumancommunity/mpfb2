"""Operator for loading an ink layer"""

import bpy
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import MaterialService
from .... import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibraryink")


class MPFB_OT_Load_Library_Ink_Operator(bpy.types.Operator):
    """Add an ink layer to the current material"""
    bl_idname = "mpfb.load_library_ink"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to asset", default="")
    object_type: StringProperty(name="object_type", description="type of the object", default="Basemesh")
    material_type: StringProperty(name="material_type", description="type of material", default="MAKESKIN")

    def execute(self, context):

        obj = context.object

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(obj)
        if not basemesh:
            self.report({'ERROR'}, "No basemesh found")
            return {'CANCELLED'}

        material = MaterialService.get_material(basemesh)

        if not material:
            self.report({'ERROR'}, "No material found")
            return {'CANCELLED'}

        material_type = MaterialService.identify_material(material)
        if material_type not in ["makeskin", "layered_skin"]:
            self.report({'ERROR'}, "Only MakeSkin and Layered Skin materials are supported")
            return {'CANCELLED'}

        MaterialService.load_ink_layer(basemesh, self.filepath)

        proxy = ObjectService.find_object_of_type_amongst_nearest_relatives(obj, "Proxymeshes")
        if proxy:
            self.report({'WARNING'}, "The ink layer was loaded, but it will not be visible on a proxy/topology mesh.")
        else:
            self.report({'INFO'}, "Ink layer was loaded: " + str(self.filepath))

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Library_Ink_Operator)
