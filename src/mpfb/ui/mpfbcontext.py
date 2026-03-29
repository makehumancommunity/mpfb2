"""Module with convenience logic for expanding context, scene properties and object properties into a flat object."""

import bpy
from ..services import ObjectService
from ..services import LogService
from ..services import SceneConfigSet
from ..entities.objectproperties import GeneralObjectProperties

_LOG = LogService.get_logger("mpfbcontext")

class ContextFocusObject:
    """When constructing a MpfbContext object, which object should be used as the focus object. This determines
    which object will be used to, for example, resolve object properties."""
    ACTIVE = 0     # The currently active object
    BASEMESH = 1   # The basemesh object amongst the nearest relatives of the active object
    PROXY = 2      # The proxymesh object amongst the nearest relatives of the active object
    ROOT = 3       # The top parent object for the character, usually the basemesh or the rig
    RIG = 4        # The rig object amongst the nearest relatives of the active object
    ARMATURE = 5   # Any armature object, even if it is not designated as a makehuman rig
    CLOTHES = 6    # The first object of type "Clothes" amongst the nearest relatives of the active object
    EYES = 7       # The first object of type "Eyes" amongst the nearest relatives of the active object
    EYELASHES = 8  # The first object of type "Eyelashes" amongst the nearest relatives of the active object
    EYEBROWS = 9   # The first object of type "Eyebrows" amongst the nearest relatives of the active object
    TONGUE = 10    # The first object of type "Tongue" amongst the nearest relatives of the active object
    TEETH = 11    # The first object of type "Teeth" amongst the nearest relatives of the active object
    HAIR = 12      # The first object of type "Hair" amongst the nearest relatives of the active object

class ContextResolveEffort:
    """How much energy should be spent on finding objects of various types amongst the nearest relatives of the active object."""
    NONE = 0    # Do not resolve any related objects. Only active_object and selected_objects will be set (if available)
    FOCUS = 1   # Only attempt to find an object of the type specified as focus type
    COMMON = 2  # Find basemesh, rig, proxy and root object amongst the nearest relatives of the active object
    ALL = 3     # Find objects of all makehuman types, as well as any related armatures amongst the nearest relatives of the active object

class MpfbContext:
    """MpfbContext is a short-lived helper class which simplifies the process of expanding context, scene properties and object properties
    into a flat structure.

    Keys which will always exist (but which might be None) are:
    - context: The current context
    - scene: The current scene
    - active_object: The currently active object
    - focus_object: The first object of the type specified as focus type amongst the nearest relatives of the active object
    - selected_objects: The currently selected objects
    - basemesh: The basemesh object amongst the nearest relatives of the active object
    - rig: The rig object amongst the nearest relatives of the active object
    - proxy: The proxymesh object amongst the nearest relatives of the active object
    - clothes: A list of all Clothes objects amongst the nearest relatives of the active object
    - eyes: The first object of type "Eyes" amongst the nearest relatives of the active object
    - eyelashes: The first object of type "Eyelashes" amongst the nearest relatives of the active object
    - eyebrows: The first object of type "Eyebrows" amongst the nearest relatives of the active object
    - tongue: The first object of type "Tongue" amongst the nearest relatives of the active object
    - teeth: The first object of type "Teeth" amongst the nearest relatives of the active object
    - hair: The first object of type "Hair" amongst the nearest relatives of the active object
    - root: The top parent object for the character, usually the basemesh or the rig

    if given scene_properties and/or object_properties, the keys of these will be transposed into the MpfbContext.
    For example, if you have a scene property "scale_factor", then it would be readable via a MpfbContext "ctx" as "ctx.scale_factor".

    Which objects are resolved depends on the effort level specifies.
    """

    def __init__(self,
                 context=None,
                 scene_properties=None, # May be a single SceneConfigSet or a list of SceneConfigSet
                 object_properties=None,
                 focus_object_type=ContextFocusObject.BASEMESH,
                 effort=ContextResolveEffort.COMMON,
                 also_resolve_general=False,
                 exception_on_duplicate_key=True):
        """Initialize MpfbContext.

        Parameters:
        - context: The current context
        - scene_properties: A SceneConfigSet or a list of SceneConfigSet
        - object_properties: A BlenderConfigSet where the entity_reference is assumed to be the focus object
        - focus_object_type: The type of object to focus on (default is BASEMESH)
        - effort: The effort to resolve objects (default is COMMON)
        - also_resolve_general: Attempt to resolve GeneralObjectProperties from the focus object (default is False)
        - exception_on_duplicate_key: Whether to raise an exception when a duplicate key is encountered (default is True)
        """

        ctx = context
        if ctx is None:
            ctx = bpy.context

        # Things which should always exist
        self.context = ctx
        self.scene = ctx.scene
        self.active_object = ctx.active_object
        self.selected_objects = ctx.selected_objects

        # Ensure these keys are present
        self.focus_object = None
        self.basemesh = None
        self.rig = None
        self.proxy = None
        self.root = None
        self.clothes = []
        self.eyes = None
        self.eyelashes = None
        self.eyebrows = None
        self.tongue = None
        self.teeth = None
        self.hair = None

        _LOG.debug("Active object", self.active_object)

        if not self.active_object or self.active_object is None:
            # No active object, we can't resolve anything
            return

        if effort >= ContextResolveEffort.FOCUS:
            type_to_resolve = None
            match focus_object_type:
                case ContextFocusObject.BASEMESH:
                    type_to_resolve = "Basemesh"
                case ContextFocusObject.RIG:
                    type_to_resolve = "Skeleton"
                case ContextFocusObject.PROXY:
                    type_to_resolve = "Proxymeshes"
                case ContextFocusObject.CLOTHES:
                    type_to_resolve = "Clothes"
                case ContextFocusObject.EYES:
                    type_to_resolve = "Eyes"
                case ContextFocusObject.EYELASHES:
                    type_to_resolve = "Eyelashes"
                case ContextFocusObject.EYEBROWS:
                    type_to_resolve = "Eyebrows"
                case ContextFocusObject.TONGUE:
                    type_to_resolve = "Tongue"
                case ContextFocusObject.TEETH:
                    type_to_resolve = "Teeth"
                case ContextFocusObject.HAIR:
                    type_to_resolve = "Hair"
            _LOG.debug("Resolving focus object of type", type_to_resolve)
            if type_to_resolve is not None:
                # It is a makehuman type, find it amongst the nearest relatives
                self.focus_object = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, type_to_resolve)
            else:
                # Special cases
                if focus_object_type == ContextFocusObject.ACTIVE:
                    self.focus_object = self.active_object
                if focus_object_type == ContextFocusObject.ROOT:
                    self.focus_object = self.active_object
                    if self.focus_object.parent:
                        self.focus_object = self.focus_object.parent
                if focus_object_type == ContextFocusObject.ARMATURE:
                    if self.active_object.type == 'ARMATURE':
                        self.focus_object = self.active_object
                    else:
                        if self.active_object.parent and self.active_object.parent.type == 'ARMATURE':
                            self.focus_object = self.active_object.parent
                        # TODO: Look through siblings too

        _LOG.debug("Focus object", self.focus_object)

        if effort >= ContextResolveEffort.COMMON:
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

        _LOG.debug("Common objects", (self.basemesh, self.rig, self.proxy, self.root))

        if effort >= ContextResolveEffort.ALL:
            self.eyes = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Eyes")
            self.eyelashes = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Eyelashes")
            self.eyebrows = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Eyebrows")
            self.tongue = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Tongue")
            self.teeth = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Teeth")
            self.hair = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Hair")
            self.clothes = []
            for clothes in ObjectService.find_related_objects(ctx.active_object):
                if ObjectService.object_is(clothes, "Clothes"):
                    self.clothes.append(clothes)

        if scene_properties is not None:
            # Might have been given a list of SceneConfigSet
            sets_to_iterate = [scene_properties] if isinstance(scene_properties, SceneConfigSet) else scene_properties

            for configset in sets_to_iterate:
                # To ensure these keys are present even if there is no scene object
                for key in configset.get_keys():
                    if hasattr(self, key):
                        _LOG.warn("A scene property will overwrite an existing key", (key, configset))
                        if exception_on_duplicate_key:
                            raise ValueError("Duplicate key in scene properties: " + str(key))
                    setattr(self, key, None)
                if self.scene is not None:
                    for key in configset.get_keys():
                        value = configset.get_value(key, entity_reference=self.scene)
                        setattr(self, key, value)

        if object_properties is not None:
            # To ensure these keys are present even if there is no focus_object
            for key in object_properties.get_keys():
                if hasattr(self, key):
                    _LOG.warn("An object property will overwrite an existing key", (key, object_properties))
                    if exception_on_duplicate_key:
                        raise ValueError("Duplicate key in object properties: " + str(key))
                setattr(self, key, None)

            obj = self.focus_object

            if obj is not None:
                for key in object_properties.get_keys():
                    value = object_properties.get_value(key, entity_reference=obj)
                    setattr(self, key, value)

        if also_resolve_general and self.focus_object is not None:
            for key in GeneralObjectProperties.get_keys():
                if hasattr(self, key):
                    _LOG.warn("A general object property will overwrite an existing key", (key, object_properties))
                    if exception_on_duplicate_key:
                        raise ValueError("Duplicate key in general object properties: " + str(key))
                setattr(self, key, None)

            obj = self.focus_object

            if obj is not None:
                for key in GeneralObjectProperties.get_keys():
                    value = GeneralObjectProperties.get_value(key, entity_reference=obj)
                    setattr(self, key, value)

        _LOG.trace("Created MpfbContext", self.__dict__)
