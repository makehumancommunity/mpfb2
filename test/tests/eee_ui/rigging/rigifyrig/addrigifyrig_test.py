"""Tests for the Add Rig Add Rigify Rig operator."""

import bpy
import pytest
from .... import dynamic_import, ObjectService, RigService, SystemService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_AddRigifyRigOperator = dynamic_import(
    "mpfb.ui.rigging.rigifyrig.operators.addrigifyrig", "MPFB_OT_AddRigifyRigOperator"
)
RIGIFY_RIG_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.rigifyrig.rigifyrigpanel", "RIGIFY_RIG_PROPERTIES"
)


def test_add_rigify_rig_is_registered():
    assert bpy.ops.mpfb.add_rigify_rig is not None
    assert MPFB_OT_AddRigifyRigOperator is not None


def test_add_rigify_rig_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_AddRigifyRigOperator.poll(bpy.context)


def test_add_rigify_rig_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_AddRigifyRigOperator.poll(bpy.context)


def test_add_rigify_rig_executes_with_basemesh():
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")
    with HumanFixture() as fixture:
        # Disable auto-generate so this test exercises the meta-rig-only path.
        RIGIFY_RIG_PROPERTIES.set_value("auto_generate", False, entity_reference=bpy.context.scene)
        try:
            mockself = MockOperatorBase()
            result = MPFB_OT_AddRigifyRigOperator.hardened_execute(mockself, bpy.context)
            assert result == {"FINISHED"}
            mockself.mock_report.assert_no_errors()
        finally:
            RIGIFY_RIG_PROPERTIES.set_value("auto_generate", True, entity_reference=bpy.context.scene)


def test_add_rigify_rig_auto_generates_full_rig_delete():
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")
    with HumanFixture() as fixture:
        RIGIFY_RIG_PROPERTIES.set_value("auto_generate", True, entity_reference=bpy.context.scene)
        RIGIFY_RIG_PROPERTIES.set_value("meta_rig_action", "delete", entity_reference=bpy.context.scene)

        try:
            mockself = MockOperatorBase()
            result = MPFB_OT_AddRigifyRigOperator.hardened_execute(mockself, bpy.context)

            assert result == {"FINISHED"}
            mockself.mock_report.assert_no_errors()

            active = bpy.context.view_layer.objects.active
            assert active is not None
            assert active.type == "ARMATURE"
            # The active object should be the generated rig, not the meta rig.
            rig_type = RigService.identify_rig(active)
            assert not rig_type.startswith("rigify."), \
                f"Active rig should be a generated rig, got {rig_type}"

            # No meta rig (object whose name ends with .metarig) should remain in the scene.
            leftover = [o for o in bpy.data.objects if o.name.endswith(".metarig")]
            assert not leftover, f"Meta rig should have been deleted, found: {[o.name for o in leftover]}"
        finally:
            RIGIFY_RIG_PROPERTIES.set_value("meta_rig_action", "hide", entity_reference=bpy.context.scene)


def test_add_rigify_rig_auto_generates_full_rig_hide():
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")
    with HumanFixture() as fixture:
        RIGIFY_RIG_PROPERTIES.set_value("auto_generate", True, entity_reference=bpy.context.scene)
        RIGIFY_RIG_PROPERTIES.set_value("meta_rig_action", "hide", entity_reference=bpy.context.scene)

        mockself = MockOperatorBase()
        result = MPFB_OT_AddRigifyRigOperator.hardened_execute(mockself, bpy.context)

        assert result == {"FINISHED"}
        mockself.mock_report.assert_no_errors()

        meta_rigs = [o for o in bpy.data.objects if o.name.endswith(".metarig")]
        assert meta_rigs, "Meta rig should still be present in the scene when hidden"
        for mr in meta_rigs:
            assert mr.hide_viewport, f"Meta rig {mr.name} should have hide_viewport=True"
            assert mr.hide_render, f"Meta rig {mr.name} should have hide_render=True"
