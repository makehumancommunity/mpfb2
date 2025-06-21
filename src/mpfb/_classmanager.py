"""This module provides a class for managing blender classes"""

import bpy
from bpy.utils import register_class, unregister_class
from .services import LogService
from . import get_preference

_LOG = LogService.get_logger("mpfb.classmanager")

def _codecheck(cls):
    """Try to perform code quality checks on classes that are about to be registered."""

    _LOG.enter()
    _LOG.debug("Performing code quality checks on", str(cls))

    if issubclass(cls, bpy.types.Operator):
        if not hasattr(cls, "bl_idname") or not cls.bl_idname.startswith("mpfb."):
            _LOG.warn("Operator name does not start with mpfb", str(cls))
        is_mpfb_operator = False
        for c in cls.__bases__:
            if "MpfbOperator" in c.__name__:
                is_mpfb_operator = True
                break
        if not is_mpfb_operator:
            _LOG.warn("Operator does not inherit from MpfbOperator", str(cls))

    if issubclass(cls, bpy.types.Panel):
        for att in ["bl_label", "bl_space_type", "bl_region_type", "bl_category"]:
            if not hasattr(cls, att):
                _LOG.warn("Panel is missing required attribute", (att, str(cls)))
        is_mpfb_panel = False
        for c in cls.__bases__:
            if "Abstract_Panel" in c.__name__:
                is_mpfb_panel = True
                break
        if not is_mpfb_panel:
            _LOG.warn("Panel does not inherit from Abstract_Panel", str(cls))

    _LOG.leave()

class ClassManager:

    """This class keeps track of blender classes and ensures that they
    get properly registered and unregistered"""

    __stack = None  # use a class attribute as classes stack
    __isinitialized = False

    def __init__(self):
        if not type(self).__isinitialized:  # Ensure ClassManager is only registered once
            _LOG.debug("initializing classmanager")
            type(self).__stack = []
            type(self).__isinitialized = True
        else:
            raise RuntimeError("ClassManager must be a singleton")

    def getClassStack(self):
        return type(self).__stack

    @classmethod
    def isinitialized(self):
        return self.__isinitialized

    @classmethod
    def add_class(cls, append_class):
        """Add a blender class to be managed"""
        _LOG.enter()
        if cls.__stack is None:
            raise RuntimeError("ClassManager is not initialized!")
        else:
            _LOG.debug("Adding class", str(append_class))
            if get_preference("mpfb_codechecks"):
                _codecheck(append_class)
            cls.__stack.append(append_class)

    @classmethod
    def register_classes(cls):
        """Iterate over all managed classes and ask blender to register
        them. This should only be called from the register() method."""
        if cls.__stack is None:
            raise RuntimeError("ClassManager is not initialized!")
        else:
            _LOG.enter()
            for reg_class in cls.__stack:
                _LOG.debug("Registering class", str(reg_class))
                register_class(reg_class)

    @classmethod
    def unregister_classes(cls):
        """Iterate over all managed classes and ask blender to unregister
        them. This should only be called from the unregister() method."""
        if cls.__stack is None:
            raise RuntimeError("ClassManager is not initialized!")
        else:
            _LOG.enter()
            for ureg_class in cls.__stack:
                _LOG.debug("Unregistering class", str(ureg_class))
                try:
                    unregister_class(ureg_class)
                except Exception as e:
                    # This often happens during unit tests, and it's not a big deal
                    _LOG.debug("Could not unregister class", (ureg_class, e))
