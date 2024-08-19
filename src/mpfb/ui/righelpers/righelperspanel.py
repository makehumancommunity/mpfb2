
import os, bpy
from mpfb._classmanager import ClassManager
from ...services import LogService
from ...services import SceneConfigSet
from ...services import UiService
from mpfb.ui.righelpers import RigHelpersProperties
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("righelpers.righelperspanel")

_LOC = os.path.dirname(__file__)
SETUP_HELPERS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
SETUP_HELPERS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(SETUP_HELPERS_PROPERTIES_DIR, prefix="SIK_")

class MPFB_PT_RigHelpersPanel(Abstract_Panel):
    bl_label = "Rig helpers"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Rig_Panel"

    def _arm_helpers(self, scene, layout):
        box = self._create_box(layout, "Arm helpers", "BONE_DATA")
        props = [
            "arm_helpers_type",
            "arm_parenting_strategy",
            "arm_target_rotates_hand",
            "arm_target_rotates_lower_arm"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)


    def _leg_helpers(self, scene, layout):
        box = self._create_box(layout, "Leg helpers", "BONE_DATA")
        props = [
            "leg_helpers_type",
            "leg_parenting_strategy",
            "leg_target_rotates_foot",
            "leg_target_rotates_lower_leg"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)

    def _finger_helpers(self, scene, layout):
        box = self._create_box(layout, "Finger helpers", "BONE_DATA")
        props = [
            "finger_helpers_type"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)

    def _eye_helpers(self, scene, layout):
        box = self._create_box(layout, "Eye helpers", "BONE_DATA")
        props = [
            "eye_ik",
            "eye_parenting_strategy"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)

    def _apply_helpers(self, scene, layout):
        box = self._create_box(layout, "Apply", "ARMATURE_DATA")
        props = [
            "hide_fk",
            "preserve_fk"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.add_helpers")

    def _remove_helpers(self, scene, layout):
        box = self._create_box(layout, "Remove", "ARMATURE_DATA")
        box.operator("mpfb.remove_helpers")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None or context.object.type != 'ARMATURE':
            return

        armature_object = context.object

        finger_mode = RigHelpersProperties.get_value("finger_mode", entity_reference=armature_object)
        leg_mode = RigHelpersProperties.get_value("leg_mode", entity_reference=armature_object)
        arm_mode = RigHelpersProperties.get_value("arm_mode", entity_reference=armature_object)
        eye_mode = RigHelpersProperties.get_value("eye_mode", entity_reference=armature_object)

        if finger_mode or leg_mode or arm_mode or eye_mode:
            self._remove_helpers(scene, layout)
        else:
            self._arm_helpers(scene, layout)
            self._leg_helpers(scene, layout)
            self._finger_helpers(scene, layout)
            self._eye_helpers(scene, layout)
            self._apply_helpers(scene, layout)


ClassManager.add_class(MPFB_PT_RigHelpersPanel)
