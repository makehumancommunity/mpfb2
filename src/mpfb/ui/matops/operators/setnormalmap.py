"""Operator for setting a normal map in a material."""

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from ....services import LogService
from ....services import MaterialService
from .... import ClassManager

_LOG = LogService.get_logger("matops.setnormalmap")

class MPFB_OT_Set_Normalmap_Operator(bpy.types.Operator, ImportHelper):
    """Adjust material by changing its normalmap or adding a normalmap to it"""
    bl_idname = "mpfb.set_normalmap"
    bl_label = "Set normalmap"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.png')

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            return True
        return False

    def execute(self, context):
        obj = context.active_object
        scn = context.scene

        if not MaterialService.has_materials(obj):
            self.report({'ERROR'}, "The selected object needs to have a material")
            return {'FINISHED'}

        material = MaterialService.get_material(obj)

        MaterialService.set_normalmap(material, self.filepath)

        self.report({'INFO'}, "Normalmap added")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Set_Normalmap_Operator)
