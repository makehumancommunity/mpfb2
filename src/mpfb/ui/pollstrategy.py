"""
This is a module for class decorator for various poll situations.

The idea is that pretty much all operators in MPFB will have a poll method, and that these
poll methods usually look very similar. Rather than repeating the same code in each poll method,
we can create a decorator that takes the poll strategy as an argument and applies it to the poll method.

The decorator as such is "@pollstrategy", while the constants with strategies is in "PollStrategy".

For example, to make an operator that checks if a basemesh can be found in a selected character, you'd use:

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MyOperator(bpy.types.Operator):
    ...

"""

import bpy
from ..services import LogService
from ..services import ObjectService

_LOG = LogService.get_logger("pollstrategy")

class PollStrategy:
    ALWAYS_TRUE = 1
    ANY_MESH_OBJECT_ACTIVE = 2
    ANY_ARMATURE_OBJECT_ACTIVE = 3
    ANY_MAKEHUMAN_OBJECT_ACTIVE = 4
    BASEMESH_ACTIVE = 5
    RIG_ACTIVE = 6
    BASEMESH_AMONGST_RELATIVES = 7
    RIG_AMONGST_RELATIVES = 8
    ACTIVE_ARMATURE_IN_POSE_MODE = 9
    ACTIVE_MESH_IN_EDIT_MODE = 10

def _ensure_context(context):
    if context is not None:
        return context
    return bpy.context

def _strategy_always_true(cls, context):
    _LOG.trace("In strategy ALWAYS_TRUE", (cls, context))
    return True

def _strategy_any_mesh_object_active(cls, context):
    _LOG.trace("In strategy ANY_MESH_OBJECT_ACTIVE", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None:
        return False
    return ObjectService.object_is_any_mesh(ctx.active_object)

def _strategy_basemesh_active(cls, context):
    _LOG.trace("In strategy BASEMESH_ACTIVE", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None:
        return False
    return ObjectService.object_is_basemesh(ctx.active_object)

def _strategy_any_armature_object_active(cls, context):
    _LOG.trace("In strategy ANY_ARMATURE_OBJECT_ACTIVE", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None:
        return False
    return ctx.active_object is not None and ctx.active_object.type == "ARMATURE"

def _strategy_any_makehuman_object_active(cls, context):
    _LOG.trace("In strategy ANY_MAKEHUMAN_OBJECT_ACTIVE", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None:
        return False
    return ObjectService.object_is_any_makehuman_object(ctx.active_object)

def _strategy_rig_active(cls, context):
    _LOG.trace("In strategy RIG_ACTIVE", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None:
        return False
    return ObjectService.object_is_any_skeleton(ctx.active_object)

def _strategy_basemesh_amongst_relatives(cls, context):
    _LOG.trace("In strategy BASEMESH_AMONGST_RELATIVES", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None or ctx.active_object is None:
        return False
    return ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Basemesh") is not None

def _strategy_rig_amongst_relatives(cls, context):
    _LOG.trace("In strategy RIG_AMONGST_RELATIVES", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None or ctx.active_object is None:
        return False
    return ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.active_object, "Skeleton") is not None

def _strategy_active_armature_in_pose_mode(cls, context):
    _LOG.trace("In strategy ACTIVE_ARMATURE_IN_POSE_MODE", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None:
        return False
    return (ctx.active_object is not None
            and ctx.active_object.type == "ARMATURE"
            and ctx.active_object.mode == "POSE")

def _strategy_active_mesh_in_edit_mode(cls, context):
    _LOG.trace("In strategy ACTIVE_MESH_IN_EDIT_MODE", (cls, context))
    ctx = _ensure_context(context)
    if ctx is None:
        return False
    return (ObjectService.object_is_any_mesh(ctx.active_object)
            and ctx.active_object.mode == "EDIT")

class pollstrategy(object):
    """A class decorator which adds a poll method to the class based on the provided poll strategy."""

    def __init__(self, strategy=PollStrategy.ALWAYS_TRUE):
        self.strategy = strategy
        _LOG.trace("init with strategy", self.strategy)

    def __call__(self, klass):
        _LOG.trace("Now decorating", klass.__name__)
        if self.strategy == PollStrategy.ALWAYS_TRUE:
            klass.poll = classmethod(_strategy_always_true)
        if self.strategy == PollStrategy.ANY_MESH_OBJECT_ACTIVE:
            klass.poll = classmethod(_strategy_any_mesh_object_active)
        if self.strategy == PollStrategy.ANY_ARMATURE_OBJECT_ACTIVE:
            klass.poll = classmethod(_strategy_any_armature_object_active)
        if self.strategy == PollStrategy.ANY_MAKEHUMAN_OBJECT_ACTIVE:
            klass.poll = classmethod(_strategy_any_makehuman_object_active)
        if self.strategy == PollStrategy.BASEMESH_ACTIVE:
            klass.poll = classmethod(_strategy_basemesh_active)
        if self.strategy == PollStrategy.RIG_ACTIVE:
            klass.poll = classmethod(_strategy_rig_active)
        if self.strategy == PollStrategy.BASEMESH_AMONGST_RELATIVES:
            klass.poll = classmethod(_strategy_basemesh_amongst_relatives)
        if self.strategy == PollStrategy.RIG_AMONGST_RELATIVES:
            klass.poll = classmethod(_strategy_rig_amongst_relatives)
        if self.strategy == PollStrategy.ACTIVE_ARMATURE_IN_POSE_MODE:
            klass.poll = classmethod(_strategy_active_armature_in_pose_mode)
        if self.strategy == PollStrategy.ACTIVE_MESH_IN_EDIT_MODE:
            klass.poll = classmethod(_strategy_active_mesh_in_edit_mode)
        return klass
