from .....services import LogService
from .....services import MaterialService
from .....services import NodeService
from .....services import ObjectService
from .....services import LocationService
from .....services import TargetService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("basemeshops.operators.bakeshapekeys")

@pollstrategy(PollStrategy.BASEMESH_ACTIVE)
class MPFB_OT_Bake_Shapekeys_Operator(bpy.types.Operator):
    """Bake all shape keys into a final mesh. WARNING: You will no longer be able to adjust targets after doing this"""
    bl_idname = "mpfb.bake_shapekeys"
    bl_label = "Bake shapekeys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'FINISHED'}

        obj = context.object

        objtype = ObjectService.get_object_type(context.object)

        if objtype != "Basemesh":
            self.report({'ERROR'}, "Can only bake shapekeys on basemesh")
            return {'FINISHED'}

        TargetService.bake_targets(context.object)

        self.report({'INFO'}, "Bake finished")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Bake_Shapekeys_Operator)
