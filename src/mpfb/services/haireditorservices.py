"""Module for convenience methods for hair editor"""

import os, bpy, json

from .logservice import LogService
from .locationservice import LocationService

_LOG = LogService.get_logger("services.haireditorservice")

class HairEditorService():
    """The HairEditorService class provides useful functions for the hair editor. All method are static methods."""

    def __init__(self):
        raise RuntimeError("You should not instance HairEditorService. Use its static methods instead.")

    @staticmethod
    def _get_hair_or_fur_blend_path(search_term="hair"):
        user_data_hair = LocationService.get_user_data("hair")
        if os.path.exists(user_data_hair):
            blend = os.path.join(user_data_hair, "haireditor", search_term + ".blend")
            _LOG.debug("User path for " + search_term + " blend", (blend, os.path.exists(blend)))
            if os.path.exists(blend) and os.path.isfile(blend):
                return os.path.realpath(os.path.abspath(blend))

        system_data_hair = LocationService.get_mpfb_data("hair")
        if os.path.exists(system_data_hair):
            blend = os.path.join(system_data_hair, "haireditor", search_term + ".blend")
            _LOG.debug("System path for " + search_term + " blend", (blend, os.path.exists(blend)))
            if os.path.exists(blend) and os.path.isfile(blend):
                _LOG.warn("Falling back to system path for hair blend, should probably move to user data folder.")
                return os.path.realpath(os.path.abspath(blend))

        _LOG.debug("No hair blend found.")
        return None

    @staticmethod
    def get_hair_blend_path():
        """Get the path to the hair blend file.

        Returns:
            str or None: The absolute path to the hair blend file if found, None otherwise.
            The function first checks in the user data directory, then falls back to the system data directory.
        """
        return HairEditorService._get_hair_or_fur_blend_path(search_term="hair")

    @staticmethod
    def get_fur_blend_path():
        """Get the path to the fur blend file.

        Returns:
            str or None: The absolute path to the fur blend file if found, None otherwise.
            The function first checks in the user data directory, then falls back to the system data directory.
        """
        return HairEditorService._get_hair_or_fur_blend_path(search_term="fur")

    @staticmethod
    def is_hair_asset_installed():
        """Check if the hair asset blend file is installed.

        Returns:
            bool: True if the hair blend file exists, False otherwise.
        """
        return HairEditorService.get_hair_blend_path() is not None

    @staticmethod
    def is_fur_asset_installed():
        """Check if the fur asset blend file is installed.

        Returns:
            bool: True if the fur blend file exists, False otherwise.
        """
        return HairEditorService.get_fur_blend_path() is not None

