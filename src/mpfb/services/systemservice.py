"""Various functionality for system and directories"""

import os, sys, subprocess, bpy, addon_utils, re
from .logservice import LogService
_LOG = LogService.get_logger("services.systemservice")

class SystemService:
    """Utility functions for various system tasks."""

    def __init__(self):
        """You should not instance SystemService. Use its static methods instead."""
        raise RuntimeError("You should not instance SystemService. Use its static methods instead.")

    @staticmethod
    def deduce_platform():
        """Deduces the current system platform (ie the operating system)."""
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
        """Open a file browser window for the specified path."""
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
        """Check if the Blender OBJ importer is installed."""
        if not hasattr(bpy.ops.import_scene, "obj"):
            return False
        (loaded_default, loaded_state) = addon_utils.check('io_scene_obj') # pylint: disable=W0612
        return loaded_state

    @staticmethod
    def check_for_rigify():
        """Check if the Blender Rigify addon is installed."""
        if not hasattr(bpy.ops.pose, "rigify_generate"):
            return False
        (loaded_default, loaded_state) = addon_utils.check('rigify') # pylint: disable=W0612
        return loaded_state

    @staticmethod
    def normalize_path_separators(path_string):
        """Replace all escaped backslashes with forward slashes."""
        if not path_string:
            return ""
        return re.sub(r"\\+", "/", str(path_string))

    @staticmethod
    def string_contains_path_segment(full_path, path_segment, case_insensitive=True):
        """Check if the full path contains the path segment."""
        if not full_path or not path_segment:
            return False
        full = SystemService.normalize_path_separators(full_path)
        path_segment = str(path_segment)
        if case_insensitive:
            full = full.lower()
            path_segment = path_segment.lower()
        segments = full.split("/")
        for segment in segments:
            if segment == path_segment:
                return True
        return False
