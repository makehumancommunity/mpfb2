"""Abstract wrapper for UI operators"""

import bpy, platform, sys, traceback
from datetime import date
from ..services import LogService
from ..services import LocationService
from ..services import ObjectService
from mpfb import VERSION, BUILD_INFO

_LOG = LogService.get_logger("uiactions")


class MpfbOperator(bpy.types.Operator):
    """Abstract wrapper for UI operators, providing help for writing error summaries"""

    def __init__(self, logname, default_log_level=None):
        """Initialize the operator. You will normally not need to call this manually."""

        bpy.types.Operator.__init__(self)

        self.LOG = LogService.get_logger(logname)
        if default_log_level is not None:
            self.LOG.set_level(default_log_level)

    def _generate_error_information(self, context, error, tb=""):
        """Generate an error information hash, providing information about the error and the state of the context."""

        out = "\n\nAn unhandled error was encountered. Please provide this info in an error report:\n\n"

        out = out + "CONTEXT\n"
        out = out + "-------\n"
        out = out + "context .............. : %s\n" % str(context)
        if context:
            out = out + "scene ................ : %s\n" % str(context.scene)
            out = out + "active_object ........ : %s\n" % str(context.active_object)
            if context.active_object:
                out = out + "active_object_mode ... : %s\n" % str(context.active_object.mode)
                out = out + "active_object_type ... : %s\n" % str(ObjectService.get_object_type(context.active_object))

        out = out + "\nOPERATOR\n"
        out = out + "--------\n"
        out = out + "name ................. : %s\n" % str(self.bl_idname)
        out = out + "label...... .......... : %s\n" % str(self.bl_label)

        out = out + "\nSYSTEM\n"
        out = out + "------\n"
        out = out + "blender_version ...... : %s\n" % str(bpy.app.version)
        out = out + "blender_version_string : %s\n" % str(bpy.app.version_string)
        out = out + "python_version ....... : %s\n" % str(sys.version)
        out = out + "platform ............. : %s\n" % str(platform.platform())
        out = out + "platform system....... : %s\n" % str(platform.system())
        out = out + "platform release...... : %s\n" % str(platform.release())

        out = out + "\nMPFB\n"
        out = out + "----\n"
        out = out + "version .............. : %s\n" % str(VERSION)
        out = out + "build ................ : %s\n" % str(BUILD_INFO)
        out = out + "data dir ............. : %s\n" % str(LocationService.get_mpfb_data())
        out = out + "mpfb dir ............. : %s\n" % str(LocationService.get_mpfb_root())
        out = out + "user dir ............. : %s\n" % str(LocationService.get_user_home())

        out = out + "\nERROR\n"
        out = out + "-----\n"
        out = out + "type ................. : %s\n" % str(type(error).__name__)
        out = out + "message .............. : %s\n" % str(error)

        out = out + "\nSTACK TRACE\n"
        out = out + "-----------\n"
        out = out + tb

        dt = date.today()
        fn = LocationService.get_log_dir("error_report_" + dt.strftime('%Y%m%d') + ".txt")

        with open(fn, "w") as f:
            f.write(out)

        out = out + "\n\nThe above error summary has also been written to: %s\n" % fn

        out = out + "\nInformation on how to report errors can be found here: "
        out = out + "http://static.makehumancommunity.org/mpfb/faq/how_do_i_report_a_bug.html\n\n"

        return out

    def execute(self, context):
        """The excute method called by blender. This will wrap the actual execute method in a try/except block. If an exception is raised, it will be logged
        and a summary of the error will be written to a log file."""
        self.LOG.enter()
        _LOG.debug("Executing %s" % self.__class__.__name__)
        try:
            return self.hardened_execute(context)
        except Exception as e:
            self.LOG.crash("Execution caused an exception", self._generate_error_information(context, e, traceback.format_exc()))
            # print(traceback.format_exc())
            self.report({'ERROR'}, "An unhandled exception was encountered: %s. See console or log for information to provide in error report." % e)
            return {'CANCELLED'}

    def hardened_execute(self, context):
        """Abstract method for the actual execute method. This will be called by the blender execute method. This method should be
        overridden by subclasses."""
        self.LOG.error("Hardened execution is not supported (subclass should override this method)")
        raise NotImplementedError("Hardened execution is not supported (subclass should override this method)")
