"""Standard rig sub-panel: pre-add controls and absorbed rig-helpers content."""

import os
from .... import ClassManager
from ....services import LogService
from ....services import RigService
from ....services import UiService
from ....services import ObjectService
from ....services import SceneConfigSet
from ...abstractpanel import Abstract_Panel
from . import RigHelpersProperties

_LOG = LogService.get_logger("standardrig.standardrigpanel")

_LOC = os.path.dirname(__file__)
STANDARD_RIG_PROPERTIES_DIR = os.path.join(_LOC, "properties")
STANDARD_RIG_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(STANDARD_RIG_PROPERTIES_DIR, prefix="ADR_")

SETUP_HELPERS_PROPERTIES_DIR = os.path.join(_LOC, "helperproperties")
SETUP_HELPERS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(SETUP_HELPERS_PROPERTIES_DIR, prefix="SIK_")


class MPFB_PT_Standard_Rig_Panel(Abstract_Panel):
    """Add a standard (non-rigify) rig, or edit rig helpers on an existing standard rig."""

    bl_label = "Standard rig"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_parent_id = "MPFB_PT_Rig_Panel"
    bl_options = {'DEFAULT_CLOSED'}

    def _add_standard_rig(self, scene, layout):
        props = [
            "standard_rig",
            "import_weights"
            ]
        STANDARD_RIG_PROPERTIES.draw_properties(scene, layout, props)
        layout.operator('mpfb.add_standard_rig')

    def _arm_helpers(self, scene, layout):
        box = self.create_box(layout, "Arm helpers")
        props = [
            "arm_helpers_type",
            "arm_parenting_strategy",
            "arm_target_rotates_hand",
            "arm_target_rotates_lower_arm"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)

    def _leg_helpers(self, scene, layout):
        box = self.create_box(layout, "Leg helpers")
        props = [
            "leg_helpers_type",
            "leg_parenting_strategy",
            "leg_target_rotates_foot",
            "leg_target_rotates_lower_leg"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)

    def _finger_helpers(self, scene, layout):
        box = self.create_box(layout, "Finger helpers")
        props = [
            "finger_helpers_type"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)

    def _eye_helpers(self, scene, layout):
        box = self.create_box(layout, "Eye helpers")
        props = [
            "eye_ik",
            "eye_parenting_strategy"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)

    def _apply_helpers(self, scene, layout):
        box = self.create_box(layout, "Apply")
        props = [
            "hide_fk",
            "preserve_fk"
            ]
        SETUP_HELPERS_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.add_helpers")

    def _remove_helpers(self, scene, layout):
        box = self.create_box(layout, "Remove")
        box.operator("mpfb.remove_helpers")

    def _draw_helpers(self, scene, layout, armature_object):
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

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if context.active_object is None:
            _LOG.debug("There is no active object")
            return

        armature_object = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        _LOG.debug("Armature object", armature_object)

        if not armature_object:
            self._add_standard_rig(scene, layout)
            return

        if ObjectService.object_is_any_skeleton(context.active_object):
            rig_type = RigService.identify_rig(context.active_object)
            if rig_type in ("default", "default_no_toes"):
                self._draw_helpers(scene, layout, context.active_object)
                return

        layout.label(text="Not applicable for the current state.")


ClassManager.add_class(MPFB_PT_Standard_Rig_Panel)
