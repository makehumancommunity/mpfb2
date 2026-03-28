"""Module with convenience logic for expanding context, scene properties and object properties into a flat object."""

import bpy
from .objectservice import ObjectService
from .logservice import LogService

_LOG = LogService.get_logger("mpfbcontext")

class MpfbContext:
    """MpfbContext is a short-lived helper class which simplifies the process of expanding context, scene properties and object properties
    into a flat structure.

    Keys which will always exist (but which might be None) are:
    - context: The current context
    - scene: The current scene
    - active_object: The currently active object
    - selected_objects: The currently selected objects
    - basemesh: The basemesh object amongst the nearest relatives of the active object
    - rig: The rig object amongst the nearest relatives of the active object
    - proxy: The proxymesh object amongst the nearest relatives of the active object
    - root: The top parent object for the character, usually the basemesh or the rig

    if given scene_properties and/or object_properties, the keys of these will be transposed into the MpfbContext.
    For example, if you have a scene property "scale_factor", then it would be readable via a MpfbContext "ctx" as "ctx.scale_factor".
    """

    def __init__(self, context=None, scene_properties=None, object_properties=None, use_basemesh_for_object_properties=True, skip_object_resolve=False):
        ctx = context
        if ctx is None:
            ctx = bpy.context

        # Things which should always exist
        self.context = ctx
        self.scene = ctx.scene
        self.active_object = ctx.active_object
        self.selected_objects = ctx.selected_objects

        # Ensure these keys are present
        self.basemesh = None
        self.rig = None
        self.proxy = None
        self.root = None

        if not skip_object_resolve and ctx.active_object is not None:
            self.basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object)
            self.rig = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Skeleton")
            self.proxy = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Proxymeshes")

            if self.basemesh is not None:
                self.root = self.basemesh
                if self.basemesh.parent:
                    self.root = self.basemesh.parent
            if self.root is None and self.rig is not None:
                self.root = self.rig
                if self.rig.parent:
                    self.root = self.rig.parent
            if self.root is None and self.proxy is not None:
                self.root = self.proxy
                if self.proxy.parent:
                    self.root = self.proxy.parent

        if scene_properties is not None:
            # To ensure these keys are present even if there is no scene object
            for key in scene_properties.get_keys():
                if hasattr(self, key):
                    _LOG.warn("A scene property will overwrite a core key", (key, scene_properties))
                setattr(self, key, None)
            if self.scene is not None:
                for key in scene_properties.get_keys():
                    value = scene_properties.get_value(key, entity_reference=self.scene)
                    setattr(self, key, value)

        if object_properties is not None:
            # To ensure these keys are present even if there is no scene object
            for key in object_properties.get_keys():
                if hasattr(self, key):
                    _LOG.warn("An object property will overwrite a core key", (key, object_properties))
                setattr(self, key, None)

            if use_basemesh_for_object_properties:
                obj = self.basemesh
            else:
                obj = self.active_object

            if obj is not None:
                for key in object_properties.get_keys():
                    value = object_properties.get_value(key, entity_reference=obj)
                    setattr(self, key, value)

        _LOG.trace("Created MpfbContext", self.__dict__)
