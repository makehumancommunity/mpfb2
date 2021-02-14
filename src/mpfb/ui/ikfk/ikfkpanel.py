#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, bpy
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.ui.ikfk import IkFkProperties

_LOG = LogService.get_logger("ikfk.ikfkpanel")

_LOC = os.path.dirname(__file__)
SETUP_IK_PROPERTIES_DIR = os.path.join(_LOC, "properties")
SETUP_IK_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(SETUP_IK_PROPERTIES_DIR, prefix="SIK_")

class MPFB_PT_Ik_Fk_Panel(bpy.types.Panel):
    bl_label = "IK / FK"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("RIGCATEGORY")

    def _create_box(self, layout, box_text, box_icon=None):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text, icon=box_icon)
        return box

    def _left_arm_ik(self, scene, layout):
        box = self._create_box(layout, "Left arm", "MODIFIER")
        props = [
            "left_arm_ik_type",
            "left_arm_preserve_fk",
            "left_arm_target_rotates_hand",
            "left_arm_target_rotates_lower_arm",
            "left_arm_hide_fk",
            "left_arm_root_parent",
            "left_arm_outmost_parent"
            ]
        SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.left_arm_ik")


    def _right_arm_ik(self, scene, layout):
        box = self._create_box(layout, "Right arm", "MODIFIER")
        props = [
            "right_arm_ik_type",
            "right_arm_preserve_fk",
            "right_arm_target_rotates_hand",
            "right_arm_target_rotates_lower_arm",
            "right_arm_hide_fk",
            "right_arm_root_parent",
            "right_arm_outmost_parent"
            ]
        SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.right_arm_ik")

    def _left_leg_ik(self, scene, layout):
        box = self._create_box(layout, "Left leg", "MODIFIER")
        props = [
            "left_leg_ik_type",
            "left_leg_preserve_fk",
            "left_leg_target_rotates_foot",
            "left_leg_target_rotates_lower_leg",
            "left_leg_hide_fk",
            "left_leg_root_parent",
            "left_leg_outmost_parent"
            ]
        SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.left_leg_ik")


    def _right_leg_ik(self, scene, layout):
        box = self._create_box(layout, "Right leg", "MODIFIER")
        props = [
            "right_leg_ik_type",
            "right_leg_preserve_fk",
            "right_leg_target_rotates_foot",
            "right_leg_target_rotates_lower_leg",
            "right_leg_hide_fk",
            "right_leg_root_parent",
            "right_leg_outmost_parent"
            ]
        SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.right_leg_ik")

    def _fingers_ik(self, scene, layout):
        box = self._create_box(layout, "Fingers", "MODIFIER")
        props = [
            "finger_ik_type",
            "finger_hide_fk"
            ]
        SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.finger_ik")

    def _fingers_fk(self, scene, layout):
        box = self._create_box(layout, "Fingers", "MODIFIER")
        props = [
            "finger_preserve_ik"
            ]
        #SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.finger_fk")

    def _left_arm_fk(self, scene, layout):
        box = self._create_box(layout, "Left arm", "MODIFIER")
        props = [
            "left_arm_preserve_ik"
            ]
        #SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.left_arm_fk")

    def _right_arm_fk(self, scene, layout):
        box = self._create_box(layout, "Right arm", "MODIFIER")
        props = [
            "right_arm_preserve_ik"
            ]
        #SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.right_arm_fk")

    def _left_leg_fk(self, scene, layout):
        box = self._create_box(layout, "Left leg", "MODIFIER")
        props = [
            "left_leg_preserve_ik"
            ]
        #SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.left_leg_fk")

    def _right_leg_fk(self, scene, layout):
        box = self._create_box(layout, "Right leg", "MODIFIER")
        props = [
            "right_leg_preserve_ik"
            ]
        #SETUP_IK_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.right_leg_fk")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        obj = context.object
        if obj is None or obj.type != 'ARMATURE':
            return

        mode = IkFkProperties.get_value("right_arm_mode", entity_reference=obj)
        if not mode:
            self._right_arm_ik(scene, layout)
        else:
            self._right_arm_fk(scene, layout)

        mode = IkFkProperties.get_value("left_arm_mode", entity_reference=obj)
        if not mode:
            self._left_arm_ik(scene, layout)
        else:
            self._left_arm_fk(scene, layout)

        mode = IkFkProperties.get_value("right_leg_mode", entity_reference=obj)
        if not mode:
            self._right_leg_ik(scene, layout)
        else:
            self._right_leg_fk(scene, layout)

        mode = IkFkProperties.get_value("left_leg_mode", entity_reference=obj)
        if not mode:
            self._left_leg_ik(scene, layout)
        else:
            self._left_leg_fk(scene, layout)

        mode = IkFkProperties.get_value("finger_mode", entity_reference=obj)
        if not mode:
            self._fingers_ik(scene, layout)
        else:
            self._fingers_fk(scene, layout)

ClassManager.add_class(MPFB_PT_Ik_Fk_Panel)
