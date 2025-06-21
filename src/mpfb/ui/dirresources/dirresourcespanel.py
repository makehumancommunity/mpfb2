"""This file contains the dir resources panel."""

from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import UiService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("dirresources.dirresourcespanel")

class MPFB_PT_Dir_Resources_Panel(Abstract_Panel):
    """UI for opening dir links."""
    bl_label = "Directories"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_System_Panel"

    def _path(self, layout, label, path):
        dirlink = layout.operator("mpfb.dir_resource", text=label)
        dirlink.path = path

    def draw(self, context):
        _LOG.enter()
        layout = self.layout

        user_files = LocationService.get_user_home()
        library_files = LocationService.get_user_data()
        system_data = LocationService.get_mpfb_data()
        log_files = LocationService.get_user_home("logs")

        self._path(layout, "User files", user_files)
        self._path(layout, "Library files", library_files)
        self._path(layout, "System data", system_data)
        self._path(layout, "Log files", log_files)


ClassManager.add_class(MPFB_PT_Dir_Resources_Panel)

