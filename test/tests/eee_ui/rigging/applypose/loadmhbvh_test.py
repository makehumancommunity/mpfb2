"""Tests for the Apply Pose Load MH BVH operator.

This operator subclasses MpfbOperator, so hardened_execute() is called instead of execute().
The operator requires a valid BVH file path; in the test environment (which sets
raise_exceptions_in_mpfboperator=True) an IOError is raised when the path is empty.
"""

import bpy
import pytest
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_Load_MH_BVH_Operator = dynamic_import(
    "mpfb.ui.rigging.applypose.operators.loadmhbvh", "MPFB_OT_Load_MH_BVH_Operator"
)


def test_load_mhbvh_is_registered():
    assert bpy.ops.mpfb.load_mhbvh_pose is not None
    assert MPFB_OT_Load_MH_BVH_Operator is not None


def test_load_mhbvh_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Load_MH_BVH_Operator.poll(bpy.context)


def test_load_mhbvh_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        assert MPFB_OT_Load_MH_BVH_Operator.poll(bpy.context)


def test_load_mhbvh_hardened_execute_raises_on_missing_file():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        mockself = MockOperatorBase(filepath="")
        with pytest.raises(IOError):
            MPFB_OT_Load_MH_BVH_Operator.hardened_execute(mockself, bpy.context)
