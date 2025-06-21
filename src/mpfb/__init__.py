"""This is the main file for MPFB. For more information about MPFB as a whole, see the README.md file in the zip.

The MPFB code is organized into several key directories, each serving a distinct purpose:

src/mpfb/entities: This directory contains the core data models and logic for different entities used in the project.
Entities represent the main objects or concepts within the application, such as materials, rigs, helpers, and other
domain-specific objects.

src/mpfb/services: The services directory contains the core logic of the project. The files contain utility classes and functions
that provide various services to the rest of the application. These services are typically stateless and provide reusable
functionality. Examples of services include logging, node management, location services, and system services. These services help in
abstracting and encapsulating common operations that can be used across different parts of the application.

src/mpfb/ui:
The ui directory is responsible for defining the user interface elements of the add-on. This includes panels, operators, and other
UI components that are integrated into Blender's interface. The UI components interact with the rest of the application, allowing
users to perform actions and configure settings through Blender's graphical interface.

src/mpfb/data:
The data directory contains static resources and data files used by the project. This can include 3D object files, textures, configuration
files, and other assets required for the add-on to function. These resources are typically loaded and used by the entities and services to
provide the necessary functionality within Blender.

The root of the project (ie this file) is the entry point for the Blender add-on. It loads and initializes the necessary modules and services.
It also exposes a few important functions and objects:

- get_preference(): Return a preference key from the MPFB preference panel
- VERSION: A tuple representing the version of MPFB
- BUILD_INFO: Build information of MPFB. It defaults to "FROM_SOURCE" if not a build, otherwise it contains the build date
- DEBUG: A boolean indicating whether debug mode is enabled. If DEBUG is True, some early initialization info is printed to the console
- MPFB_CONTEXTUAL_INFORMATION: A dictionary containing contextual information of the addon, such as in which package it was loaded
- ClassManager: A singleton object that manages the registration and unregistering of classes such as panels and operators
"""

fake_bl_info = {  # pylint: disable=C0103
    "name": "mpfb",
    "author": "Joel Palmius",
    "version": (2, 0, 10),
    "blender": (4, 2, 0),
    "location": "View3D > Properties > MPFB",
    "description": "Free and open source human character editor",
    "doc_url": "http://static.makehumancommunity.org/mpfb.html",
    "tracker_url": "https://github.com/makehumancommunity/mpfb2/issues",
    "category": "MakeHuman"}

# These are constants that can be imported from submodules
VERSION = fake_bl_info["version"]
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

import bpy, os
from bpy.utils import register_class

# For printing output before _LOG has been initialized
DEBUG = False


def get_preference(name):
    """
    Retrieve a preference value from the MPFB preference panel.

    This function looks up a preference value by its name from the MPFB add-on's preferences.
    If the preference is found, its value is returned. If the preference is not found, an error
    message is printed, and None is returned. If the add-on or its preferences are not properly
    initialized, a ValueError is raised.

    Args:
        name (str): The name of the preference to retrieve.

    Returns:
        The value of the preference if found, otherwise None.

    Raises:
        ValueError: If the add-on or its preferences are not properly initialized.
    """
    global DEBUG  # pylint: disable=W0602
    if DEBUG:
        print("get_preference(\"" + name + "\")")
    if __package__ in bpy.context.preferences.addons:
        mpfb = bpy.context.preferences.addons[__package__]
        if hasattr(mpfb, "preferences"):
            prefs = mpfb.preferences
            if hasattr(prefs, name):
                value = getattr(prefs, name)
                if DEBUG:
                    print("Found addon preference", (name, value))
                return value
            print("There were addon preferences, but key did not exist:", name)
            print("preferences", dir(prefs))
            print("hasattr", hasattr(prefs, name))
            print("name in", name in prefs)
            return None
        print("The '" + __package__ + "' addon does not have any preferences!?")
        raise ValueError("Preferences have not been initialized properly")
    print("The '" + __package__ + "' addon does not exist!?")
    raise ValueError("I don't seem to exist")


ClassManager = None

# To get around the limitation where the extension platform only allows us to use relative imports, we will populate a
# structure with information about the root package, and references to some of the most important classes.
MPFB_CONTEXTUAL_INFORMATION = None


def register():
    """At this point blender is ready enough for it to make sense to
    start initializing python singletons"""

    global _LOG  # pylint: disable=W0603

    # To allow other code structures (primarily the unit test code) access to MPFB's logic without knowing
    # anything about the module structure, store info about the package and the location of the root py.
    #
    # One might have assumed that bpy.app.driver_namespace would be good place to store this, but that gets wiped
    # when loading a new blend file. Instead something like the following is needed:
    #
    # import importlib
    # for amod in sys.modules:
    #    if amod.endswith("mpfb"):
    #        mpfb_mod = importlib.import_module(amod)
    #        print(mpfb_mod.MPFB_CONTEXTUAL_INFORMATION)
    #
    # Sample usage of this can be seen in test/tests/__init__.py
    global MPFB_CONTEXTUAL_INFORMATION
    MPFB_CONTEXTUAL_INFORMATION = dict()
    MPFB_CONTEXTUAL_INFORMATION["__package__"] = str(__package__)
    MPFB_CONTEXTUAL_INFORMATION["__package_short__"] = str(__package__).split(".")[-1]
    MPFB_CONTEXTUAL_INFORMATION["__file__"] = str(__file__)

    # Preferences will be needed before starting the rest of the addon
    from ._preferences import MpfbPreferences
    try:
        register_class(MpfbPreferences)
    except:
        print("WARNING: Could not register preferences class. Maybe it was registered by an earlier version of MPFB?")

    from .services import LogService  # This will also cascade import the other services
    _LOG = LogService.get_logger("mpfb.init")
    _LOG.info("Build info", "FROM_SOURCE")
    _LOG.reset_timer()

    # ClassManager is a singleton to which all modules can add their
    # Blender classes, preferably when the module is imported the first
    # time. Thus we'll import all packages which can theoretically
    # contain blender classes.

    from ._classmanager import ClassManager as _ClassManager
    global ClassManager
    ClassManager = _ClassManager

    if not ClassManager.isinitialized():
        classmanager = ClassManager()  # pylint: disable=W0612
        _LOG.debug("classmanager", classmanager)

    _LOG.debug("About to import mpfb.ui")
    from .ui import UI_DUMMY_VALUE  # pylint: disable=W0612

    _LOG.debug("After imports")

    # We can now assume all relevant classes have been added to the
    # class manager singleton.

    _LOG.debug("About to request class registration")
    ClassManager.register_classes()

    from .services import SystemService

    if SystemService.is_blender_version_at_least():
        _LOG.debug("About to check if MakeHuman is online")

        if bpy.app.online_access:
            # Try to find out where the makehuman user data is at
            from .services import LocationService, SocketService
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
        else:
            _LOG.info("Online access preference is not enabled. Not checking if MakeHuman is online.")

    from .services import SERVICES
    MPFB_CONTEXTUAL_INFORMATION["SERVICES"] = SERVICES

    _LOG.time("Number of milliseconds to run entire register() method:")
    _LOG.info("MPFB initialization has finished.")


def unregister():
    """Deconstruct all loaded blenderish classes"""

    global _LOG  # pylint: disable=W0603,W0602

    _LOG.debug("About to unregister classes")
    global ClassManager  # pylint: disable=W0603,W0602
    ClassManager.unregister_classes()


__all__ = ["VERSION", "DEBUG", "BUILD_INFO", "ClassManager", "MPFB_CONTEXTUAL_INFORMATION"]
