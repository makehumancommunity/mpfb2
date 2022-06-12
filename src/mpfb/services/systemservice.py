"""Various functionality for system and directories"""

import os, sys, subprocess, bpy, addon_utils
from .logservice import LogService
_LOG = LogService.get_logger("services.systemservice")

class SystemService:
    """Utility functions for various system tasks."""

    def __init__(self):
        """You should not instance SystemService. Use its static methods instead."""
        raise RuntimeError("You should not instance SystemService. Use its static methods instead.")

    @staticmethod
    def deduce_platform():
        if sys.platform.startswith('linux'):
            return "LINUX"

        if sys.platform.startswith('win32'):
            return "WINDOWS"

        if sys.platform.startswith('cygwin'):
            return "WINDOWS"

        if sys.platform.startswith('darwin'):
            return "MACOS"

        # Default to windows, since that's the most likely platform
        return "WINDOWS"

    @staticmethod
    def open_file_browser(path):
        platform = SystemService.deduce_platform()
        if platform == "LINUX":
            subprocess.call(["xdg-open", path])
            return
        if platform == "WINDOWS":
            os.startfile(path) # pylint: disable=E1101
            return
        raise NotImplementedError("Opening a file browser is not supported for platform " + platform)

    @staticmethod
    def check_for_obj_importer():
        if not hasattr(bpy.ops.import_scene, "obj"):
            return False

        for module in addon_utils.modules():
            print(module)

        (loaded_default, loaded_state) = addon_utils.check('io_scene_obj')
        return loaded_state


