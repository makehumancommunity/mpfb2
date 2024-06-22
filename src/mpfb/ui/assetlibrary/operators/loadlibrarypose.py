"""Operator for importing poses from asset library."""

import bpy
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb.services.animationservice import AnimationService
from mpfb import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibrarypose")

class MPFB_OT_Load_Library_Pose_Operator(bpy.types.Operator):
    """Load Pose from asset library"""
    bl_idname = "mpfb.load_library_pose"
    bl_label = "Load Pose"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to asset", default="")
    object_type: StringProperty(name="object_type", description="type of the object", default="Pose")

    def execute(self, context):
        _LOG.debug("filepath", self.filepath)

        blender_object = context.active_object

        if not blender_object or blender_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature")
            return {'CANCELLED'}

        if not ObjectService.object_is_skeleton(blender_object):
            self.report({'ERROR'}, "Active object is not identified as a skeleton")
            return {'CANCELLED'}

        try:
            AnimationService.import_bvh_file_as_pose(blender_object, self.filepath)
            self.report({'INFO'}, "Pose loaded successfully")
        except Exception as e:
            _LOG.error("Failed to load pose", e)
            self.report({'ERROR'}, f"Failed to load pose: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Pose_Operator)