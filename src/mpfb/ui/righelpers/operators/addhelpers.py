from mpfb.services.logservice import LogService
#from mpfb.entities.fingerik.fingerik import FingerIk
from mpfb.ui.righelpers import RigHelpersProperties
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("setupikoperators.fingerfk")

class MPFB_OT_AddHelpersOperator(bpy.types.Operator):
    """This will add all selected helpers to the active armature"""
    bl_idname = "mpfb.add_helpers"
    bl_label = "Add helpers"
    bl_options = {'REGISTER', 'UNDO'}

    def _arm_helpers(self, armature_object, settings):
        from mpfb.services.righelpers.armhelpers.armhelpers import ArmHelpers
        for side in ["left", "right"]:
            helpers = ArmHelpers.get_instance(side, settings)
            helpers.apply_ik(armature_object)
        RigHelpersProperties.set_value("arm_mode", settings["arm_helpers_type"], entity_reference=armature_object)

    def _leg_helpers(self, armature_object, settings):
        from mpfb.services.righelpers.leghelpers.leghelpers import LegHelpers
        for side in ["left", "right"]:
            helpers = LegHelpers.get_instance(side, settings)
            helpers.apply_ik(armature_object)
        RigHelpersProperties.set_value("leg_mode", settings["leg_helpers_type"], entity_reference=armature_object)

    def _finger_helpers(self, armature_object, settings):
        from mpfb.services.righelpers.fingerhelpers.fingerhelpers import FingerHelpers
        for side in ["left", "right"]:
            helpers = FingerHelpers.get_instance(side, settings)
            helpers.apply_ik(armature_object)
        RigHelpersProperties.set_value("finger_mode", settings["finger_helpers_type"], entity_reference=armature_object)

    def execute(self, context):
        _LOG.enter()
        armature_object = context.object

        from mpfb.ui.righelpers.righelperspanel import SETUP_HELPERS_PROPERTIES # pylint: disable=C0415
        settings = SETUP_HELPERS_PROPERTIES.as_dict(entity_reference=context.scene)

        if "arm_helpers_type" in settings and settings["arm_helpers_type"] and settings["arm_helpers_type"] != "NONE":
            _LOG.debug("Adding arm helpers:", settings["arm_helpers_type"])
            self._arm_helpers(armature_object, settings)
        else:
            _LOG.debug("Not adding arm helpers")

        if "leg_helpers_type" in settings and settings["leg_helpers_type"] and settings["leg_helpers_type"] != "NONE":
            _LOG.debug("Adding leg helpers:", settings["leg_helpers_type"])
            self._leg_helpers(armature_object, settings)
        else:
            _LOG.debug("Not adding leg helpers")

        if "finger_helpers_type" in settings and settings["finger_helpers_type"] and settings["finger_helpers_type"] != "NONE":
            _LOG.debug("Adding finger helpers:", settings["finger_helpers_type"])
            self._finger_helpers(armature_object, settings)
        else:
            _LOG.debug("Not adding finger helpers")

        self.report({'INFO'}, "Helpers were added")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        # TODO: check current mode
        return True

ClassManager.add_class(MPFB_OT_AddHelpersOperator)
