#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.entities.legik.legik import LegIk
from mpfb.ui.ikfk import IkFkProperties
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("setupikoperators.leftlegik")

class MPFB_OT_LeftLegIkOperator(bpy.types.Operator):
    """This will apply the specificied IK settings to the active armature's left leg"""
    bl_idname = "mpfb.left_leg_ik"
    bl_label = "Convert to IK"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _LOG.enter()
        armature_object = context.object

        from mpfb.ui.ikfk.ikfkpanel import SETUP_IK_PROPERTIES # pylint: disable=C0415
        settings = SETUP_IK_PROPERTIES.as_dict(entity_reference=context.scene)
        legik = LegIk.get_instance("left", settings)
        legik.apply_ik(armature_object)

        IkFkProperties.set_value("left_leg_mode", settings["left_leg_ik_type"], entity_reference=armature_object)

        self.report({'INFO'}, "Left leg was set to IK")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        mode = IkFkProperties.get_value("left_leg_mode", entity_reference=context.object)
        if not mode:
            return True # Undefined or space means FK
        return False

ClassManager.add_class(MPFB_OT_LeftLegIkOperator)
