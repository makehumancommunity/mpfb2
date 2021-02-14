
import os, bpy, time, pprint, inspect

# There's a catch 22 where paths should be read from the location
# service, but the location service is dependent on the log service

_BPYHOME = bpy.utils.resource_path('USER') # pylint: disable=E1111
_MPFBHOME = os.path.join(_BPYHOME, "mpfb")
_LOGDIR = os.path.abspath(os.path.join(_MPFBHOME, "logs"))
_COMBINED = os.path.join(_LOGDIR, "combined.txt")

print("\nInitializing MPFB log service. Logs can be found in " + str(_LOGDIR) + "\n")

if not os.path.exists(_LOGDIR):
    os.makedirs(_LOGDIR, exist_ok=True)

_JUSTIFICATION = 35
_START = int(time.time() * 1000.0)


class Logger():

    def __init__(self, name, level=5):
        self.name = name
        self.level = level
        self.path = os.path.join(_LOGDIR, "separated." + name + ".txt")
        self.time_stamp = _START
        with open(self.path, "w") as log_file:
            log_file.write("")

    def _log_message(self, level, message, extra_object=None):
        if level <= self.level:
            extra = ""
            if not extra_object is None:
                extra = " " + str(extra_object)
            location = str(self.name + " ").ljust(_JUSTIFICATION, ".") + ": "
            long_message = "[" + LogService.LOGLEVELS[level] + "] " + location + message + extra
            short_message = "[" + LogService.LOGLEVELS[level] + "] " + message + extra
            print(long_message)
            with open(self.path, "a") as log_file:
                log_file.write(short_message + "\n")
            with open(_COMBINED, "a") as log_file:
                log_file.write(long_message + "\n")

    def set_level(self, level):
        self.level = level

    def crash(self, message, extra_object=None):
        self._log_message(LogService.CRASH, message, extra_object)

    def error(self, message, extra_object=None):
        self._log_message(LogService.ERROR, message, extra_object)

    def warn(self, message, extra_object=None):
        self._log_message(LogService.WARN, message, extra_object)

    def info(self, message, extra_object=None):
        self._log_message(LogService.INFO, message, extra_object)

    def debug(self, message, extra_object=None):
        self._log_message(LogService.DEBUG, message, extra_object)

    def trace(self, message, extra_object=None):
        self._log_message(LogService.TRACE, message, extra_object)

    def dump(self, message, extra_object):
        if self.level > LogService.TRACE:
            if isinstance(extra_object, str):
                serialized_object = "\n" + extra_object
            else:
                serialized_object = "\n" + pprint.pformat(extra_object, 4, 180, depth=5)
            self._log_message(LogService.DUMP, message, serialized_object)

    def enter(self):
        if self.level >= LogService.TRACE:
            info = dict()
            stack = inspect.currentframe().f_back
            info["line_number"] = str(stack.f_lineno)
            info["caller_name"] = stack.f_globals["__name__"]
            info["file_name"] = stack.f_globals["__file__"]
            info["caller_method"] = inspect.stack()[1][3]
            message = "Now entering {}.{}():{}".format(info["caller_name"], info["caller_method"], info["line_number"])
            self._log_message(LogService.TRACE, message)

    def get_current_time(self):
        return int(time.time() * 1000.0) - self.time_stamp

    def time(self, message):
        current = int(time.time() * 1000.0)
        self._log_message(LogService.DEBUG, message, current - self.time_stamp)

    def reset_timer(self):
        self.time_stamp = int(time.time() * 1000.0)


class LogService():

    LOGLEVELS = ["CRASH", "ERROR", "WARN ", "INFO ", "DEBUG", "TRACE", "DUMP "]
    CRASH = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5
    DUMP = 6  # For putting very large objects into log output

    def __init__(self):
        raise RuntimeError("You should not instance LogService. Use its static methods instead.")

    @staticmethod
    def get_logger(name):
        return _LOGSERVICE.get_or_create_log_channel(str(name))

    @staticmethod
    def set_default_log_level(level):
        _LOGSERVICE.set_default_log_level(level)


class _LogService():

    def __init__(self):
        self._loggers = dict()
        self._default_log_level = LogService.TRACE
        with open(_COMBINED, "w") as log_file:
            log_file.write("")

    def get_or_create_log_channel(self, name):
        if not name in self._loggers:
            self._loggers[name] = Logger(name, self._default_log_level)
        return self._loggers[name]

    def set_default_log_level(self, level):
        self._default_log_level = level
        for logger in self._loggers.values():
            logger.set_level(level)


_LOGSERVICE = _LogService()
