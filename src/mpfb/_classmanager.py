#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides a class for managing blender classes"""

from bpy.utils import register_class, unregister_class

from mpfb.services import LogService
LOG = LogService.get_logger("mpfb.classmanager")

class ClassManager:

    """This class keeps track of blender classes and ensures that they
    get properly registered and unregistered"""

    __initialized = False # ensure ClassManager is only registered once
    __stack = None # use a class attribute as classes stack

    def __init__(self):
        if not type(self).__initialized:
            LOG.debug("initializing classmanager")
            type(self).__initialized = True
            type(self).__stack = []
        else:
            raise RuntimeError("ClassManager must be a singleton")

    def getClassStack(self):
        return type(self).__stack

    @classmethod
    def add_class(cls, appendClass):
        """Add a blender class to be managed"""
        LOG.enter()
        if cls.__stack is None:
            raise RuntimeError("ClassManager is not initialized!")
        else:
            LOG.debug("Adding class", str(appendClass))
            cls.__stack.append(appendClass)

    @classmethod
    def register_classes(cls):
        """Iterate over all managed classes and ask blender to register
        them. This should only be called from the register() method."""
        if cls.__stack is None:
            raise RuntimeError("ClassManager is not initialized!")
        else:
            LOG.enter()
            for regClass in cls.__stack:
                LOG.debug("Registering class", str(regClass))
                register_class(regClass)

    @classmethod
    def unregister_classes(cls):
        """Iterate over all managed classes and ask blender to unregister
        them. This should only be called from the unregister() method."""
        if cls.__stack is None:
            raise RuntimeError("ClassManager is not initialized!")
        else:
            LOG.enter()
            for uregClass in cls.__stack:
                LOG.debug("Unregistering class", str(uregClass))
                unregister_class(uregClass)

