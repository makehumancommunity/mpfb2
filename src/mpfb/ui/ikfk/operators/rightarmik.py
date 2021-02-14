#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.entities.armik.armik import ArmIk
from mpfb.ui.ikfk import IkFkProperties
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("setupikoperators.rightarmik")

_RADIAN = 0.0174532925

class MPFB_OT_RightArmIkOperator(bpy.types.Operator):
    """This will apply the specificied IK settings to the active armature's right arm"""
    bl_idname = "mpfb.right_arm_ik"
    bl_label = "Convert to IK"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _LOG.enter()
        armature_object = context.object

        from mpfb.ui.ikfk.ikfkpanel import SETUP_IK_PROPERTIES # pylint: disable=C0415
        settings = SETUP_IK_PROPERTIES.as_dict(entity_reference=context.scene)
        armik = ArmIk.get_instance("right", settings)
        armik.apply_ik(armature_object)

        IkFkProperties.set_value("right_arm_mode", settings["right_arm_ik_type"], entity_reference=armature_object)

        self.report({'INFO'}, "Right arm was set to IK")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        mode = IkFkProperties.get_value("right_arm_mode", entity_reference=context.object)
        if not mode:
            return True # Undefined or space means FK
        return False

ClassManager.add_class(MPFB_OT_RightArmIkOperator)
