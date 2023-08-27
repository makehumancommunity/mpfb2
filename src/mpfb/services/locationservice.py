import os, bpy
from mpfb import get_preference
from .logservice import LogService
from pathlib import Path

_LOG = LogService.get_logger("services.locationservice")

class _LocationService():

    def __init__(self):
        _LOG.debug("Constructing location service")
        self._bpy_home = os.path.abspath(bpy.utils.resource_path('USER'))

        self._user_home = os.path.join(self._bpy_home, "mpfb")
        overriden_user_home = None
        try:
            overriden_user_home = get_preference("mpfb_user_data")
        except:
            _LOG.warn("Could not read preference mpfb_user_data")
        _LOG.debug("overriden_user_home", overriden_user_home)
        if overriden_user_home:
            self._user_home = overriden_user_home

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

        self._mh_user_data = None
        self._mh_auto_user_data = False
        self._check_set_mh_user_dir()

        self._user_data = os.path.join(self._user_home, "data")
        self._user_config = os.path.join(self._user_home, "config")

        self._log_dir = os.path.join(self._user_home, "logs")

        script_location = os.path.dirname(__file__)

        self._mpfb_root = Path(os.path.join(script_location, "..")).resolve()

        self._repo_src = os.path.abspath(os.path.realpath(os.path.join(self._mpfb_root, '..')))
        self._repo_root = os.path.abspath(os.path.join(self._repo_src, '..'))
        self._test_root = os.path.abspath(os.path.join(self._repo_root, 'test'))

        self._mpfb_data = os.path.join(self._mpfb_root, "data")

        self._relevant_directories = []
        self._relevant_directories.append(self._bpy_home)
        self._relevant_directories.append(self._user_home)
        self._relevant_directories.append(self._user_data)
        self._relevant_directories.append(self._user_config)

        self._relevant_directories.append(self._log_dir)

        self._relevant_directories.append(self._mpfb_root)
        self._relevant_directories.append(self._mpfb_data)

    def _check_set_mh_user_dir(self):
        _LOG.enter()
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
                _LOG.warn("mh_user_dir is not explicitly set, and autodiscovery is enabled")
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
                        else:
                            _LOG.debug("Mh user data is not at", full_path)
            else:
                _LOG.info("mh_user_dir is not explicitly set but autodiscovery is disabled")
        else:
            _LOG.info("mh_user_data explicitly set to", mh_user_data)
            self._mh_user_data = mh_user_data

    def update_mh_user_data_if_relevant(self, new_path):
        if self._mh_auto_user_data:
            self._mh_user_data = new_path

    def ensure_relevant_directories_exist(self):
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

    def _return_path(self, path, sub_path=None):
        _LOG.enter()
        _LOG.trace("_return_path, path is", path)
        _LOG.trace("_return_path, sub_path is", sub_path)
        if sub_path is None:
            return path
        return os.path.join(path, sub_path)

    def get_user_home(self, sub_path=None):
        _LOG.enter()
        return self._return_path(self._user_home, sub_path)

    def get_user_data(self, sub_path=None):
        _LOG.enter()
        return self._return_path(self._user_data, sub_path)

    def get_user_config(self, sub_path=None):
        _LOG.enter()
        return self._return_path(self._user_config, sub_path)

    def get_mpfb_data(self, sub_path=None):
        _LOG.enter()
        return self._return_path(self._mpfb_data, sub_path)

    def get_mpfb_root(self, sub_path=None):
        _LOG.enter()
        return self._return_path(self._mpfb_root, sub_path)

    def get_second_root(self, sub_path=None):
        _LOG.enter()
        if not self._second_root:
            return None
        return self._return_path(self._second_root, sub_path)

    def get_log_dir(self, sub_path=None):
        _LOG.enter()
        return self._return_path(self._log_dir, sub_path)

    def get_mh_user_data(self, sub_path=None):
        _LOG.enter()
        if not self.is_mh_user_data_enabled():
            return None
        return self._return_path(self._mh_user_data, sub_path)

    def get_mpfb_test(self, sub_path=None):
        _LOG.enter()
        return self._return_path(self._test_root, sub_path)

    def is_source_dist(self):
        return os.path.exists(self._test_root)

    def is_mh_user_data_enabled(self):
        return self._mh_user_data is not None

    def is_mh_auto_user_data_enabled(self):
        return self._mh_auto_user_data


LocationService = _LocationService() # pylint: disable=C0103
LocationService.ensure_relevant_directories_exist()
