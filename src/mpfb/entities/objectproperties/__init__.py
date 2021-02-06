#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module sets up and provide global custom properties for blender objects,
for example of what type a certain object is. See JSON data under "generalproperties"
for information about the actual properties"""

import bpy, os

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("objectproperties.init")
_LOG.trace("initializing object properties module")

from mpfb.services.blenderconfigset import BlenderConfigSet

_ROOT = os.path.dirname(__file__)

_GENERAL_PROPERTIES_DIR = os.path.join(_ROOT, "generalproperties")
_GENERAL_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_GENERAL_PROPERTIES_DIR)

# This is the object that can be imported
GeneralObjectProperties = BlenderConfigSet(_GENERAL_PROPERTIES, bpy.types.Object) # pylint: disable=C0103

__all__ = [
    "GeneralObjectProperties"
    ]
