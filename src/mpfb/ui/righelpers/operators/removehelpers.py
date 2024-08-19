from ....services import LogService
# from mpfb.entities.fingerik.fingerik import FingerIk
from ...righelpers import RigHelpersProperties
from .... import ClassManager
from ....entities.rigging.righelpers.armhelpers.armhelpers import ArmHelpers
from ....entities.rigging.righelpers.leghelpers.leghelpers import LegHelpers
from ....entities.rigging.righelpers.fingerhelpers.fingerhelpers import FingerHelpers
from ....entities.rigging.righelpers.eyehelpers.eyehelpers import EyeHelpers
import bpy

_LOG = LogService.get_logger("setupikoperators.fingerfk")


class MPFB_OT_RemoveHelpersOperator(bpy.types.Operator):
    """This will remove all helpers from the active armature"""
    bl_idname = "mpfb.remove_helpers"
    bl_label = "Remove helpers"
    bl_options = {'REGISTER', 'UNDO'}

    def _arm_helpers(self, armature_object, settings):
        for side in ["left", "right"]:
            helpers = ArmHelpers.get_instance(side, settings)
            helpers.remove_ik(armature_object)
        RigHelpersProperties.set_value("arm_mode", "", entity_reference=armature_object)

    def _leg_helpers(self, armature_object, settings):
        for side in ["left", "right"]:
            helpers = LegHelpers.get_instance(side, settings)
            helpers.remove_ik(armature_object)
        RigHelpersProperties.set_value("leg_mode", "", entity_reference=armature_object)

    def _finger_helpers(self, armature_object, settings):
        for side in ["left", "right"]:
            helpers = FingerHelpers.get_instance(side, settings)
            helpers.remove_ik(armature_object)
        RigHelpersProperties.set_value("finger_mode", "", entity_reference=armature_object)

    def _eye_helpers(self, armature_object, settings):
        helpers = EyeHelpers.get_instance(settings)
        helpers.remove_ik(armature_object)
        RigHelpersProperties.set_value("eye_mode", "", entity_reference=armature_object)

    def execute(self, context):
        _LOG.enter()
        armature_object = context.object

        from ...righelpers.righelperspanel import SETUP_HELPERS_PROPERTIES  # pylint: disable=C0415
        settings = SETUP_HELPERS_PROPERTIES.as_dict(entity_reference=context.scene)

        finger_mode = RigHelpersProperties.get_value("finger_mode", entity_reference=armature_object)
        leg_mode = RigHelpersProperties.get_value("leg_mode", entity_reference=armature_object)
        arm_mode = RigHelpersProperties.get_value("arm_mode", entity_reference=armature_object)
        eye_mode = RigHelpersProperties.get_value("eye_mode", entity_reference=armature_object)

        if finger_mode:
            self._finger_helpers(armature_object, settings)

        if leg_mode:
            self._leg_helpers(armature_object, settings)

        if arm_mode:
            self._arm_helpers(armature_object, settings)

        if eye_mode:
            self._eye_helpers(armature_object, settings)

        self.report({'INFO'}, "Helpers were removed")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False

        armature_object = context.object

        finger_mode = RigHelpersProperties.get_value("finger_mode", entity_reference=armature_object)
        leg_mode = RigHelpersProperties.get_value("leg_mode", entity_reference=armature_object)
        arm_mode = RigHelpersProperties.get_value("arm_mode", entity_reference=armature_object)
        eye_mode = RigHelpersProperties.get_value("eye_mode", entity_reference=armature_object)

        return finger_mode or leg_mode or arm_mode or eye_mode


ClassManager.add_class(MPFB_OT_RemoveHelpersOperator)
