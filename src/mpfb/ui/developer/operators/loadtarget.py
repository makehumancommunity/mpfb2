import os
import bpy

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty, FloatProperty, BoolProperty
from ....services import LogService
from ....services import ObjectService
from ....services import TargetService
from .... import ClassManager

_LOG = LogService.get_logger("developer.operators.loadtarget")


class MPFB_OT_Load_Target_Operator(bpy.types.Operator, ImportHelper):
    """Import one or more targets as shape keys"""
    bl_idname = "mpfb.load_target"
    bl_label = "Load targets"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.target;*.ptarget;*.target.gz;*.ptarget.gz', options={'HIDDEN'})
    directory: StringProperty(options={'HIDDEN'})
    files: CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement)

    weight: FloatProperty(name="Weight", default=1.0, min=0.0, max=1.0,
                          description="Initial weight to be assigned for the new shape keys")
    encode: BoolProperty(name="Encode Names", default=False,
                         description="Encode mpfb macro detail names according to the standard rules")

    @classmethod
    def poll(cls, context):
        return ObjectService.object_is_basemesh(context.active_object)

    def draw(self, context):
        self.layout.operator("file.select_all", text="Select/Deselect All").action = 'TOGGLE'
        self.layout.prop(self, 'weight')
        self.layout.prop(self, 'encode')

    def execute(self, context):
        blender_object = context.active_object
        filenames = [os.path.join(self.directory, f.name) for f in self.files]

        if not filenames:
            self.report({'ERROR'}, 'No file is selected for import')
            return {'CANCELLED'}

        for name in filenames:
            if not os.path.isfile(name):
                self.report({'ERROR'}, f'Non-file selected for import: {os.path.basename(name)}')
                return {'CANCELLED'}

        for name in filenames:
            if self.encode:
                shape_name = TargetService.filename_to_shapekey_name(name, macrodetail=None)
            else:
                shape_name = TargetService.filename_to_shapekey_name(name)

            TargetService.load_target(blender_object, name, weight=self.weight, name=shape_name)

        self.report({'INFO'}, "Targets were imported as shape keys")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Target_Operator)
