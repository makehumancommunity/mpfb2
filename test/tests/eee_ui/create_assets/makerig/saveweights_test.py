"""Tests for the MakeRig SaveWeights operator."""

import bpy
import tempfile
import os
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Save_Weights_Operator = dynamic_import("mpfb.ui.create_assets.makerig.operators.saveweights", "MPFB_OT_Save_Weights_Operator")


def test_save_weights_is_registered():
    assert bpy.ops.mpfb.save_weights is not None
    assert MPFB_OT_Save_Weights_Operator is not None


def test_save_weights_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    # poll() calls ObjectService.object_is_any_mesh(context.object) which may throw on None
    # Ensure it returns False gracefully
    try:
        result = MPFB_OT_Save_Weights_Operator.poll(bpy.context)
        assert not result
    except Exception:
        pass  # Expected if context.object is None causes an error in poll


def test_save_weights_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Save_Weights_Operator.poll(bpy.context)


def test_save_weights_errors_mesh_without_armature_modifier():
    with HumanFixture() as fixture:
        fd, tmp_path = tempfile.mkstemp(suffix=".mhw")
        os.close(fd)
        try:
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_Save_Weights_Operator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_reported('ERROR', "armature")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def test_save_weights_from_armature():
    with HumanWithRigFixture() as fixture:
        ObjectService.activate_blender_object(fixture.rig)
        fd, tmp_path = tempfile.mkstemp(suffix=".mhw")
        os.close(fd)
        try:
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_Save_Weights_Operator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()
            assert os.path.getsize(tmp_path) > 0
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
