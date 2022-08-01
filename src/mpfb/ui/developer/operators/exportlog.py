"""Functionality for exporting log files"""

from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
from bpy_extras.io_utils import ExportHelper
import bpy, shutil

_LOG = LogService.get_logger("developer.exportlog")

class MPFB_OT_Export_Log_Operator(bpy.types.Operator, ExportHelper):
    """Export log to file"""
    bl_idname = "mpfb.export_log"
    bl_label = "Export log"
    bl_options = {'REGISTER'}

    filename_ext = '.txt'

    def execute(self, context):
        _LOG.enter()

        loggers = LogService.get_loggers()

        scene = context.scene
        from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES # pylint: disable=C0415

        logger_name = DEVELOPER_PROPERTIES.get_value("available_loggers", entity_reference=scene)

        if logger_name == "default":
            input_path = LogService.get_path_to_combined_log_file()
        else:
            logger = LogService.get_logger(logger_name)
            input_path = logger.get_path_to_log_file()

        output_path = bpy.path.abspath(self.filepath)

        shutil.copy(input_path, output_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Export_Log_Operator)
