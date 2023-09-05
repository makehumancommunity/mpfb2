"""This is the MakeHuman Plugin For Blender (MPFB). For more information, see
the README.md file in the zip."""

bl_info = { # pylint: disable=C0103
    "name": "mpfb",
    "author": "Joel Palmius",
    "version": (2, 0, 4),
    "blender": (4, 0, 0),
    "warning": "Plugin is in Alpha stage",
    "location": "View3D > Properties > MPFB",
    "description": "MakeHuman Plugin For Blender",
    "doc_url": "http://static.makehumancommunity.org/mpfb.html",
    "tracker_url": "https://github.com/makehumancommunity/mpfb2/issues",
    "category": "MakeHuman"}

# These are constants that can be imported from submodules
VERSION = bl_info["version"]
BUILD_INFO = "FROM_SOURCE"

# Don't import this log object. Instead, get a local logger via LogService
_LOG = None

# WARNING!!!
# Do not try to import anything from anywhere outside of the register method.
# We can only rely on singletons in the rest of the module being initialized
# and available once blender has gotten far enough as to call register.
#
# Because of this we will also disable pylint's warning about these imports
# pylint: disable=C0415
#
# We will also disable warnings about unused imports, since the point of
# importing here is to just make sure everything is up and running
# pylint: disable=W0611

import bpy, os, sys, traceback
from bpy.utils import register_class

_OLD_EXCEPTHOOK = None

def log_crash(type, value, tb):
    global _OLD_EXCEPTHOOK
    stacktrace = "\n"
    for line in traceback.extract_tb(tb).format():
        stacktrace = stacktrace + line
    _LOG.error("Unhandled crash", stacktrace + "\n" + str(value) + "\n")
    if _OLD_EXCEPTHOOK:
        _OLD_EXCEPTHOOK(type, value, tb)

def get_preference(name):
    _LOG.enter()
    if "mpfb" in bpy.context.preferences.addons:
        mpfb = bpy.context.preferences.addons['mpfb']
        if hasattr(mpfb, "preferences"):
            prefs = mpfb.preferences
            if hasattr(prefs, name):
                value = getattr(prefs, name)
                _LOG.debug("Found addon preference", (name, value))
                return value
            _LOG.error("There were addon preferences, but key did not exist:", name)
            _LOG.error("preferences", dir(prefs))
            _LOG.error("hasattr", hasattr(prefs, name))
            _LOG.error("name in", name in prefs)
            return None
        _LOG.crash("The 'mpfb' addon does not have any preferences")
        raise ValueError("Preferences have not been initialized properly")
    _LOG.crash("The 'mpfb' addon does not exist!?")
    raise ValueError("I don't seem to exist")

ClassManager = None

def register():
    """At this point blender is ready enough for it to make sense to
    start initializing python singletons"""

    # Preferences will be needed before starting the rest of the addon
    from ._preferences import MpfbPreferences
    try:
        register_class(MpfbPreferences)
    except:
        print("WARNING: Could not register preferences class. Maybe it was registered by an earlier version of MPFB?")

    global _LOG # pylint: disable=W0603
    global _OLD_EXCEPTHOOK # pylint: disable=W0603

    from mpfb.services.logservice import LogService
    _LOG = LogService.get_logger("mpfb.init")
    _LOG.info("Build info", "FROM_SOURCE")
    _LOG.reset_timer()
    _LOG.debug("We're in register() and about to start registering classes.")

    if get_preference("mpfb_excepthook"):
        _LOG.warn("Overriding the global exception handler. You should probably disable this when not needing it.")
        _OLD_EXCEPTHOOK = sys.excepthook
        sys.excepthook = log_crash

    # ClassManager is a singleton to which all modules can add their
    # Blender classes, preferably when the module is imported the first
    # time. Thus we'll import all packages which can theoretically
    # contain blender classes.

    from ._classmanager import ClassManager as _ClassManager
    global ClassManager
    ClassManager = _ClassManager

    if not ClassManager.isinitialized():
        classmanager = ClassManager() # pylint: disable=W0612

    _LOG.debug("About to import mpfb.services")
    import mpfb.services.locationservice
    import mpfb.services.socketservice
    import mpfb.services.uiservice

    _LOG.debug("About to import mpfb.ui")
    import mpfb.ui

    _LOG.debug("After imports")

    # We can now assume all relevant classes have been added to the
    # class manager singleton.

    _LOG.debug("About to request class registration")
    ClassManager.register_classes()

    _LOG.debug("About to check if MakeHuman is online")

    # Try to find out where the makehuman user data is at
    from mpfb.services.locationservice import LocationService
    from mpfb.services.socketservice import SocketService
    if LocationService.is_mh_auto_user_data_enabled():
        mh_user_dir = None
        try:
            mh_user_dir = SocketService.get_user_dir()
            _LOG.info("Socket service says makeHuman user dir is at", mh_user_dir)
            if mh_user_dir and os.path.exists(mh_user_dir):
                mh_user_data = os.path.join(mh_user_dir, "data")
                LocationService.update_mh_user_data_if_relevant(mh_user_data)
        except ConnectionRefusedError as err:
            _LOG.error("Could not read mh_user_dir. Maybe socket server is down? Error was:", err)
            mh_user_dir = None

    #===========================================================================
    # mh_sys_dir = None
    # try:
    #     mh_sys_dir = SocketService.get_sys_dir()
    #     _LOG.info("MakeHuman sys dir is", mh_sys_dir)
    # except ConnectionRefusedError as err:
    #     _LOG.error("Could not read mh_sys_dir. Maybe socket server is down? Error was:", err)
    #     mh_sys_dir = None
    #===========================================================================

    _LOG.time("Number of milliseconds to run entire register() method:")
    _LOG.info("MPFB initialization has finished.")


def unregister():
    """Deconstruct all loaded blenderish classes"""

    global _LOG # pylint: disable=W0603

    _LOG.debug("About to unregister classes")
    global ClassManager
    ClassManager.unregister_classes()


__all__ = ["VERSION"]
