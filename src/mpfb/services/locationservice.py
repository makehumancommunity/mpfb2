
import os, bpy

from .logservice import LogService
_LOG = LogService.get_logger("services.locationservice")


class _LocationService():

    def __init__(self):
        _LOG.debug("Constructing location service")
        self._bpy_home = os.path.abspath(bpy.utils.resource_path('USER'))

        self._user_home = os.path.join(self._bpy_home, "mpfb")
        self._user_data = os.path.join(self._user_home, "data")
        self._user_config = os.path.join(self._user_home, "config")

        self._log_dir = os.path.join(self._user_home, "logs")

        script_location = os.path.dirname(__file__)

        self._mpfb_root = os.path.abspath(os.path.join(script_location, ".."))

        self._mpfb_data = os.path.join(self._mpfb_root, "data")

        self._relevant_directories = []
        self._relevant_directories.append(self._bpy_home)
        self._relevant_directories.append(self._user_home)
        self._relevant_directories.append(self._user_data)
        self._relevant_directories.append(self._user_config)

        self._relevant_directories.append(self._log_dir)

        self._relevant_directories.append(self._mpfb_root)
        self._relevant_directories.append(self._mpfb_data)

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

    def get_log_dir(self, sub_path=None):
        _LOG.enter()
        return self._return_path(self._log_dir, sub_path)


LocationService = _LocationService() # pylint: disable=C0103
LocationService.ensure_relevant_directories_exist()
