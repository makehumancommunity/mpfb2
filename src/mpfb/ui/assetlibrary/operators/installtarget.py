"""Operator for importing a custom target."""

import bpy, os, shutil
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb import ClassManager

_LOG = LogService.get_logger("assetlibrary.installtarget")

class MPFB_OT_Install_Target_Operator(bpy.types.Operator, ImportHelper):
    """Install a custom target from a target file. Note that Blender need to be restarted for the 
    target to be visible in the custom target list"""
    bl_idname = "mpfb.install_target"
    bl_label = "Install custom target"
    bl_options = {'REGISTER'}

    filter_glob: StringProperty(default='*.target', options={'HIDDEN'})

    def execute(self, context):

        if not self.filepath:
            self.report({'ERROR'}, "Must select a file")
            return {'FINISHED'}

        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "File does not exist?")
            return {'FINISHED'}

        _LOG.debug("filepath", self.filepath)
                
        custom_dir = LocationService.get_user_data("custom")
        
        _LOG.debug("custom_dir", custom_dir)
        
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir)
            
        target = os.path.join(custom_dir, os.path.basename(self.filepath))
        
        _LOG.debug("target", target)
        
        shutil.copy(self.filepath, target)
    
        self.report({'INFO'}, "The target has been installed, but Blender needs to be restarted for it to be visible.")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Install_Target_Operator)
