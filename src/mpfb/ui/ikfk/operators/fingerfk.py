#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.entities.fingerik.fingerik import FingerIk
from mpfb.ui.ikfk import IkFkProperties
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("setupikoperators.fingerfk")

class MPFB_OT_FingerFkOperator(bpy.types.Operator):
    """This will clear all IK settings from the active armature's fingers"""
    bl_idname = "mpfb.finger_fk"
    bl_label = "Convert to FK"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _LOG.enter()
        armature_object = context.object

        from mpfb.ui.ikfk.ikfkpanel import SETUP_IK_PROPERTIES # pylint: disable=C0415
        settings = SETUP_IK_PROPERTIES.as_dict(entity_reference=context.scene)

        for side in ["left", "right"]:
            fingerik = FingerIk.get_instance(side, settings)
            fingerik.remove_ik(armature_object)

        IkFkProperties.set_value("finger_mode", "", entity_reference=armature_object)

        self.report({'INFO'}, "Fingers were set to FK")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        mode = IkFkProperties.get_value("finger_mode", entity_reference=context.object)
        if mode:
            return True # Undefined or space means FK
        return False

ClassManager.add_class(MPFB_OT_FingerFkOperator)
