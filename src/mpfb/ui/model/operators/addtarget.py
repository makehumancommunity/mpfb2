"""Operator for adding a target."""

import bpy, os, gzip
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService
from mpfb import ClassManager

_LOG = LogService.get_logger("model.addtarget")
_LOG.set_level(LogService.DUMP)

class MPFB_OT_AddTargetOperator(bpy.types.Operator):
    """Add this target as a new shape key"""

    bl_idname = "mpfb.add_target"
    bl_label = "Add target"
    bl_options = {'REGISTER', 'UNDO'}

    target_file = StringProperty(name='target_file', default='-')
    target_name = StringProperty(name='target_name', default='-')
    target_dir = StringProperty(name='target_dir', default='-')

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            return ObjectService.object_is_basemesh(context.active_object)
        return False

    @classmethod
    def description(cls, context, properties):
        return "Add the " + properties.target_name + " target as a new shape key"

    def execute(self, context):
        scene = context.scene

        if not ObjectService.object_is_basemesh(context.active_object):
            self.report({'INFO'}, "Targets can only be added to the base mesh")

        basemesh = context.active_object

        full_path = os.path.join(self.target_dir, self.target_file)

        weight = 0.5
        name = os.path.basename(full_path)
        name = name.replace(".target.gz", "")

        with gzip.open(full_path, "rb") as gzip_file:
            raw_data = gzip_file.read()
            target_string = raw_data.decode('utf-8')
            _LOG.dump("Target string", target_string)
            if not target_string is None:
                shape_key = TargetService.target_string_to_shape_key(target_string, name, basemesh)
                _LOG.dump("shape key", shape_key)
                shape_key.value = weight
            else:
                raise ValueError("Target string is None")

        self.report({'INFO'}, "Added target file " + str(full_path) + " as new shape key")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_AddTargetOperator)

