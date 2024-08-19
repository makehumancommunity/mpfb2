import gzip
import os
import re

import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from ....services import LogService
from ....services import ObjectService
from ....services import TargetService
from .... import ClassManager

_LOG = LogService.get_logger("developer.operators.savetarget")


class MPFB_OT_Save_Target_Operator(bpy.types.Operator, ExportHelper):
    """Write the active shape key as a target file"""
    bl_idname = "mpfb.save_target"
    bl_label = "Save target"
    bl_options = {'REGISTER'}

    filename_ext = '.target'

    filter_glob: StringProperty(default='*.target;*.ptarget;*.target.gz;*.ptarget.gz', options={'HIDDEN'})
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the file",
                             maxlen=1024, subtype='FILE_PATH')

    include_header: BoolProperty(name="Include Header", default=False,
                                 description="Include the boilerplate MakeTarget header")

    @staticmethod
    def get_active_key(blender_object):
        index = blender_object.active_shape_key_index
        key_blocks = blender_object.data.shape_keys.key_blocks
        if 0 < index < len(key_blocks):
            return key_blocks[index]

    @classmethod
    def poll(cls, context):
        active_object = context.active_object

        if not ObjectService.object_is_basemesh(active_object):
            return False

        return bool(cls.get_active_key(active_object))

    def invoke(self, context, event):
        active_object = context.active_object
        shape_key = self.get_active_key(active_object)

        name = TargetService.decode_shapekey_name(shape_key.name)
        name = re.sub(r'^macrodetail-', "", name)

        extension = ".target"

        if shape_key.name.startswith("$md-"):
            extension = ".target.gz"

        self.filepath = bpy.path.clean_name(name, replace="-") + extension
        return super().invoke(context, event)

    def draw(self, context):
        self.layout.prop(self, 'include_header')

    def check(self, _context):
        filepath = self.filepath

        # Override base class to allow all valid extensions
        if os.path.basename(filepath):
            if not re.search(r'\.p?target(\.gz)?$', filepath):
                filepath = bpy.path.ensure_ext(
                    os.path.splitext(filepath)[0],
                    self.filename_ext,
                )
                if filepath != self.filepath:
                    self.filepath = filepath
                    return True

        return False

    def execute(self, context):
        blender_object = context.active_object
        shape_key = self.get_active_key(blender_object)

        info = TargetService.get_shape_key_as_dict(blender_object, shape_key)

        _LOG.dump("Shape key", info)

        key_string = TargetService.shape_key_info_as_target_string(info, include_header=self.include_header)

        if self.filepath.endswith(".gz"):
            with gzip.open(self.filepath, "wb") as gzip_file:
                gzip_file.write(key_string.encode('utf-8'))
        else:
            with open(self.filepath, "w") as target_file:
                target_file.write(key_string)

        self.report({'INFO'}, "Target was saved as " + str(self.filepath))
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Target_Operator)
