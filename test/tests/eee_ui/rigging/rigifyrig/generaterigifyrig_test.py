"""Tests for the Generate Rigify Rig operator and the RigService helper it delegates to.

The poll requires a rigify meta-rig to be active. In environments without the Rigify addon
enabled, the happy-path tests are skipped via SystemService.check_for_rigify().
"""

import bpy
import pytest
from .... import dynamic_import, HumanService, ObjectService, RigService, SystemService
from ..._helpers import HumanFixture, HumanWithRigFixture, MockOperatorBase

MPFB_OT_GenerateRigifyRigOperator = dynamic_import(
    "mpfb.ui.rigging.rigifyrig.operators.generaterigifyrig",
    "MPFB_OT_GenerateRigifyRigOperator",
)


def test_generate_rigify_rig_is_registered():
    assert bpy.ops.mpfb.generate_rigify_rig is not None
    assert MPFB_OT_GenerateRigifyRigOperator is not None


def test_generate_rigify_rig_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_GenerateRigifyRigOperator.poll(bpy.context)


def test_generate_rigify_rig_poll_false_with_standard_rig():
    # A standard (non-rigify) rig should not satisfy the poll
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        assert not MPFB_OT_GenerateRigifyRigOperator.poll(bpy.context)


def test_generate_rigify_rig_helper_produces_generated_rig():
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    with HumanFixture() as fixture:
        meta_rig = HumanService.add_builtin_rig(fixture.basemesh, "rigify.human")
        assert meta_rig is not None
        assert RigService.identify_rig(meta_rig).startswith("rigify.")
        meta_rig_name = meta_rig.name

        rigify_object = RigService.generate_rigify_rig(meta_rig, delete_meta_rig=True)

        assert rigify_object is not None
        assert rigify_object.type == "ARMATURE"
        assert not RigService.identify_rig(rigify_object).startswith("rigify.")
        # delete_meta_rig=True should remove the meta rig from the scene
        assert meta_rig_name not in bpy.data.objects


def test_generate_rigify_rig_helper_keeps_meta_rig_when_requested():
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    with HumanFixture() as fixture:
        meta_rig = HumanService.add_builtin_rig(fixture.basemesh, "rigify.human")
        meta_rig_name = meta_rig.name

        rigify_object = RigService.generate_rigify_rig(meta_rig, delete_meta_rig=False)

        assert rigify_object is not None
        assert meta_rig_name in bpy.data.objects


def test_generate_rigify_rig_operator_smoke():
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    with HumanFixture() as fixture:
        meta_rig = HumanService.add_builtin_rig(fixture.basemesh, "rigify.human")
        ObjectService.activate_blender_object(meta_rig)

        mockself = MockOperatorBase()
        result = MPFB_OT_GenerateRigifyRigOperator.hardened_execute(mockself, bpy.context)

        assert result == {"FINISHED"}
        mockself.mock_report.assert_no_errors()
        active = bpy.context.view_layer.objects.active
        assert active is not None
        assert active.type == "ARMATURE"
        assert not RigService.identify_rig(active).startswith("rigify.")
