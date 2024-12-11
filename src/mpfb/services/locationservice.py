"""Module for resolving various locations as paths."""

import os, bpy
from .. import get_preference
from .. import MPFB_CONTEXTUAL_INFORMATION
from .logservice import LogService
from pathlib import Path
from typing import Optional

_LOG = LogService.get_logger("services.locationservice")


class _LocationService():
    """
    The LocationService class is designed to manage and resolve various file system paths used by the MPFB.
    It handles the initialization and configuration of directories such as user home, user data, user config,
    user cache, log directory, MPFB root, and MakeHuman user data.

    The class provides methods to update these paths based on user preferences and ensures that all relevant directories exist.
    Additionally, it supports autodiscovery of the MakeHuman user data directory if explicitly set or enabled through preferences.

    The class also includes utility methods to retrieve specific paths, optionally appending sub-paths, and to check the status
    of certain configurations like source distribution and MakeHuman user data enablement.
    """

    def __init__(self):
        _LOG.debug("Constructing location service")
        self._bpy_home = os.path.abspath(bpy.utils.resource_path('USER'))

        _LOG.debug("self._bpy_home", self._bpy_home)
        self._user_home = os.path.join(self._bpy_home, MPFB_CONTEXTUAL_INFORMATION["__package_short__"])
        _LOG.debug("self._user_home", self._user_home)

        overriden_user_home = None
        try:
            overriden_user_home = get_preference("mpfb_user_data")
        except:
            _LOG.warn("Could not read preference mpfb_user_data")
        _LOG.debug("overriden_user_home", overriden_user_home)
        if overriden_user_home:
            self._user_home = overriden_user_home

        self._check_set_second_root()
        self._check_set_mh_user_dir()

        self._user_data = os.path.join(self._user_home, "data")
        _LOG.debug("self._user_data", self._user_data)

        self._user_config = os.path.join(self._user_home, "config")
        _LOG.debug("self._user_config", self._user_config)

        self._user_cache = os.path.join(self._user_home, "cache")
        _LOG.debug("self._user_cache", self._user_cache)

        self._log_dir = os.path.join(self._user_home, "logs")
        _LOG.debug("self._log_dir", self._log_dir)

        script_location = os.path.dirname(__file__)

        self._mpfb_root = Path(os.path.join(script_location, "..")).resolve()
        _LOG.debug("self._mpfb_root", self._mpfb_root)

        self._repo_src = os.path.abspath(os.path.realpath(os.path.join(self._mpfb_root, '..')))
        _LOG.debug("self._repo_src", self._repo_src)

        self._repo_root = os.path.abspath(os.path.join(self._repo_src, '..'))
        _LOG.debug("self._repo_root", self._repo_root)

        self._test_root = os.path.abspath(os.path.join(self._repo_root, 'test'))
        _LOG.debug("self._test_root", self._test_root)

        self._mpfb_data = os.path.join(self._mpfb_root, "data")
        _LOG.debug("self._mpfb_data", self._mpfb_data)

        self._relevant_directories = []
        self._relevant_directories.append(self._bpy_home)
        self._relevant_directories.append(self._user_home)
        self._relevant_directories.append(self._user_data)
        self._relevant_directories.append(self._user_config)
        self._relevant_directories.append(self._user_cache)

        self._relevant_directories.append(self._log_dir)

        self._relevant_directories.append(self._mpfb_root)
        self._relevant_directories.append(self._mpfb_data)

    def update_mh_data(self):
        """
        Updates the MakeHuman user data location based on the current configuration.
        """
        _LOG.debug("Config change: Update MH data location")
        self._check_set_mh_user_dir()

    def update_second_root(self):
        """
        Updates the second root location based on the current configuration.
        """
        _LOG.debug("Config change: Update second root location")
        self._check_set_second_root()

    def _check_set_second_root(self):
        self._second_root = None
        try:
            self._second_root = get_preference("mpfb_second_root")
            if self._second_root is not None:
                self._second_root = str(self._second_root).strip()
                if self._second_root:
                    self._second_root = os.path.abspath(self._second_root)
                else:
                    self._second_root = None
        except:
            _LOG.warn("Could not read preference mpfb_second_root")
        _LOG.debug("second root", self._second_root)

    def _check_set_mh_user_dir(self):
        _LOG.enter()
        self._mh_user_data = None
        self._mh_auto_user_data = False
        mh_user_data = None
        try:
            mh_user_data = get_preference("mh_user_data")
        except:
            _LOG.warn("Could not read preference mh_user_data")

        if mh_user_data is not None:
            mh_user_data = mh_user_data.strip()

        if not mh_user_data:
            mh_auto_user_data = False
            try:
                mh_auto_user_data = get_preference("mh_auto_user_data")
            except:
                _LOG.warn("Could not read preference mh_auto_user_data")

            if mh_auto_user_data:
                self._mh_auto_user_data = True
                _LOG.info("Will attempt to autodiscover mh user data via local paths")
                home = str(Path.home())
                if os.path.exists(home):
                    # Very primitive routine for finding the usual suspects for the makehuman home dir.
                    # The better options are explicitly setting it in the preferences or, failing that,
                    # letting MH figure out the location via a socket call
                    check_subdirs = ["Document", "Documents", "document", "documents", "Dokument", "dokument", "."]
                    for subdir in check_subdirs:
                        full_path = os.path.join(home, subdir, "makehuman", "v1py3", "data")
                        if os.path.exists(full_path):
                            full_path = os.path.abspath(os.path.realpath(full_path))
                            _LOG.info("Autodiscovered mh user data at", full_path)
                            self._mh_user_data = full_path
                            break

                        _LOG.debug("Mh user data is not at", full_path)
            else:
                _LOG.info("Not adding link to MakeHuman user data, since neither explicit path nor auto-discovery is set in preferences.")
        else:
            _LOG.info("mh_user_data explicitly set to", mh_user_data)
            self._mh_user_data = mh_user_data

    def update_mh_user_data_if_relevant(self, new_path):
        """
        Updates the MakeHuman user data path if autodiscovery is enabled.

        Args:
            new_path (str): The new path to be set for MakeHuman user data.
        """
        if self._mh_auto_user_data:
            self._mh_user_data = new_path

    def ensure_relevant_directories_exist(self):
        """
        Ensures that all relevant directories exist. If any directory does not exist, it will be created.
        If a directory cannot be created, an IOError is raised.

        Raises:
            IOError: If a relevant directory cannot be created.
        """
        _LOG.enter()
        for dir_path in self._relevant_directories:
            if os.path.exists(dir_path):
                _LOG.debug("Relevant directory already exists:", dir_path)
            else:
                _LOG.info("Creating relevant directory:", dir_path)
                os.makedirs(dir_path, exist_ok=True)

        for dir_path in self._relevant_directories:
            if not os.path.exists(dir_path):
                _LOG.error("Was not able to create relevant directory:", dir_path)
                raise IOError('Could not create ' + dir_path)

    def _return_path(self, path, sub_path: Optional[str] = None) -> str:
        _LOG.enter()
        _LOG.trace("_return_path, path is", path)
        _LOG.trace("_return_path, sub_path is", sub_path)
        if sub_path is None:
            return path
        return os.path.join(path, sub_path)

    def get_user_home(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the user home directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the user home directory. Defaults to None.

        Returns:
            str: The full path to the user home directory or the specified sub-path within it.
        """
        _LOG.enter()
        return self._return_path(self._user_home, sub_path)

    def get_user_data(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the user data directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the user data directory. Defaults to None.

        Returns:
            str: The full path to the user data directory or the specified sub-path within it.
        """
        _LOG.enter()
        return self._return_path(self._user_data, sub_path)

    def get_user_config(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the user config directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the user config directory. Defaults to None.

        Returns:
            str: The full path to the user config directory or the specified sub-path within it.
        """
        _LOG.enter()
        return self._return_path(self._user_config, sub_path)

    def get_user_cache(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the user cache directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the user cache directory. Defaults to None.

        Returns:
            str: The full path to the user cache directory or the specified sub-path within it.
        """
        _LOG.enter()
        return self._return_path(self._user_cache, sub_path)

    def get_mpfb_data(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the MPFB data directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the MPFB data directory. Defaults to None.

        Returns:
            str: The full path to the MPFB data directory or the specified sub-path within it.
        """
        _LOG.enter()
        return self._return_path(self._mpfb_data, sub_path)

    def get_mpfb_root(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the MPFB root directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the MPFB root directory. Defaults to None.

        Returns:
            str: The full path to the MPFB root directory or the specified sub-path within it.
        """
        _LOG.enter()
        return self._return_path(self._mpfb_root, sub_path)

    def get_second_root(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the second root directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the second root directory. Defaults to None.

        Returns:
            str: The full path to the second root directory or the specified sub-path within it, or None if the second root is not set.
        """
        _LOG.enter()
        sr = self._second_root

        if bpy.context and hasattr(bpy.context, "scene") and bpy.context.scene:
            from ..ui.assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES
            src = ASSET_SETTINGS_PROPERTIES.get_value("second_root", entity_reference=bpy.context.scene)
            if str(src).strip():
                sr = str(src).strip()
                _LOG.debug("Fetched second_root from scene", ("'" + str(sr) + "'", os.path.exists(sr)))
        _LOG.debug("Returning second_root", sr)

        if not sr:
            return None

        return self._return_path(sr, sub_path)

    def get_log_dir(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the log directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the log directory. Defaults to None.

        Returns:
            str: The full path to the log directory or the specified sub-path within it.
        """
        _LOG.enter()
        return self._return_path(self._log_dir, sub_path)

    def get_mh_user_data(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the MakeHuman user data directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the MakeHuman user data directory. Defaults to None.

        Returns:
            str: The full path to the MakeHuman user data directory or the specified sub-path within it, or None if MakeHuman user data is not enabled.
        """
        _LOG.enter()
        if not self.is_mh_user_data_enabled():
            return None
        return self._return_path(self._mh_user_data, sub_path)

    def get_mpfb_test(self, sub_path: Optional[str] = None) -> str:
        """
        Returns the path to the MPFB test directory, optionally appending a sub-path.

        Args:
            sub_path (str, optional): A sub-path to append to the MPFB test directory. Defaults to None.

        Returns:
            str: The full path to the MPFB test directory or the specified sub-path within it.
        """
        _LOG.enter()
        return self._return_path(self._test_root, sub_path)

    def is_source_dist(self):
        """
        Checks if the current distribution is a source distribution.

        Returns:
            bool: True if the current distribution is a source distribution, False otherwise.
        """
        return os.path.exists(self._test_root)

    def is_mh_user_data_enabled(self):
        """
        Checks if MakeHuman user data is enabled.

        Returns:
            bool: True if MakeHuman user data is enabled, False otherwise.
        """
        return self._mh_user_data is not None

    def is_mh_auto_user_data_enabled(self):
        """
        Checks if MakeHuman user data autodiscovery is enabled.

        Returns:
            bool: True if MakeHuman user data autodiscovery is enabled, False otherwise.
        """
        return self._mh_auto_user_data


LocationService = _LocationService()  # pylint: disable=C0103
LocationService.ensure_relevant_directories_exist()
