"""Operator for creating a new human object."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
#from mpfb.ui.maketarget import MakeHumanObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("newhuman.createhuman")

class MPFB_OT_CreateHumanOperator(bpy.types.Operator):
    """Create a new human"""
    bl_idname = "mpfb.create_human"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        from mpfb.ui.newhuman.newhumanpanel import NEW_HUMAN_PROPERTIES
        from mpfb.ui.newhuman import NewHumanObjectProperties
        from mpfb.entities.objectproperties import GeneralObjectProperties

        basemesh = ObjectService.load_base_mesh(context)
        bpy.ops.object.shade_smooth()

        scale_factor = NEW_HUMAN_PROPERTIES.get_value("scale_factor", entity_reference=context.scene)

        scale = 0.1

        if scale_factor == "DECIMETER":
            scale = 1.0

        if scale_factor == "CENTIMETER":
            scale = 10.0

        bpy.ops.transform.resize(value=(scale, scale, scale))

        self.report({'INFO'}, "Human created")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateHumanOperator)
