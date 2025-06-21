"""Operator for importing MHMAT material."""

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ....entities.material.makeskinmaterial import MakeSkinMaterial
from ....services import LogService
from ....services import MaterialService
from .... import ClassManager

_LOG = LogService.get_logger("makeskin.importmaterial")

class MPFB_OT_ImportMaterialOperator(bpy.types.Operator, ImportHelper):
    """Import MHMAT"""
    bl_idname = "mpfb.import_makeskin_material"
    bl_label = "Import material"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.mhmat', options={'HIDDEN'})

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

        from ...makeskin.makeskinpanel import MAKESKIN_PROPERTIES

        if MaterialService.has_materials(obj):
            if not MAKESKIN_PROPERTIES.get_value("overwrite", entity_reference=scn):
                self.report({'ERROR'}, "A material for this object already exists, change 'replace' option in common settings to overwrite material")
                return {'FINISHED'}
            else:
                while len(obj.data.materials) > 0:
                    obj.data.materials.pop(index=0)

        material = MaterialService.create_empty_material("makeskinmaterial", obj)

        mhmat = MakeSkinMaterial()
        mhmat.populate_from_mhmat(self.filepath)
        mhmat.apply_node_tree(material)


        self.report({'INFO'}, "Material imported")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ImportMaterialOperator)
