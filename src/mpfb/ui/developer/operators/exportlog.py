"""Functionality for exporting log files"""

from ....services import LogService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from bpy_extras.io_utils import ExportHelper
import bpy, shutil

_LOG = LogService.get_logger("developer.exportlog")

class MPFB_OT_Export_Log_Operator(MpfbOperator, ExportHelper):
    """Export log to file"""
    bl_idname = "mpfb.export_log"
    bl_label = "Export log"
    bl_options = {'REGISTER'}

    filename_ext = '.txt'

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        loggers = LogService.get_loggers()

        from ...developer.developerpanel import DEVELOPER_PROPERTIES  # pylint: disable=C0415
        from ....mpfbcontext import MpfbContext

        ctx = MpfbContext(context=context, scene_properties=DEVELOPER_PROPERTIES)

        logger_name = ctx.available_loggers

        if logger_name == "default":
            input_path = LogService.get_path_to_combined_log_file()
        else:
            logger = LogService.get_logger(logger_name)
            input_path = logger.get_path_to_log_file()

        output_path = bpy.path.abspath(self.filepath)

        shutil.copy(input_path, output_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Export_Log_Operator)
