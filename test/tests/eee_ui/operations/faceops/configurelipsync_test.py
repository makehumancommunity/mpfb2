"""Tests for the FaceOps Configure Lip Sync operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Configure_Lip_Sync_Operator = dynamic_import(
    "mpfb.ui.operations.faceops.operators.configurelipsync",
    "MPFB_OT_Configure_Lip_Sync_Operator"
)


def test_configure_lip_sync_is_registered():
    assert bpy.ops.mpfb.configure_lip_sync is not None
    assert MPFB_OT_Configure_Lip_Sync_Operator is not None


def test_configure_lip_sync_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Configure_Lip_Sync_Operator.poll(bpy.context)


def test_configure_lip_sync_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Configure_Lip_Sync_Operator.poll(bpy.context)


# TODO: Functionality tests will require lipsync addon, maybe it can be mocked?

