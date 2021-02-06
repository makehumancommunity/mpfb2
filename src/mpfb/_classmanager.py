#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides a class for managing blender classes"""

from bpy.utils import register_class, unregister_class

from mpfb.services import LogService
LOG = LogService.get_logger("mpfb.classmanager")

class ClassManager:

    """This class keeps track of blender classes and see to it that they
    get properly registered and unregistered"""

    def __init__(self):
        LOG.debug("constructing classmanager")
        self._stack = []

    def add_class(self, cls):
        """Add a blender class to be managed"""
        LOG.enter()
        LOG.debug("Adding class", str(cls))
        self._stack.append(cls)

    def register_classes(self):
        """Iterate over all managed classes and ask blender to register
        them. This should only be called from the register() method."""
        LOG.enter()
        for cls in self._stack:
            LOG.debug("Registering class", str(cls))
            register_class(cls)

    def unregister_classes(self):
        """Iterate over all managed classes and ask blender to unregister
        them. This should only be called from the unregister() method."""
        LOG.enter()
        for cls in self._stack:
            LOG.debug("Unregistering class", str(cls))
            unregister_class(cls)

