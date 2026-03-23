"""Tests for the FaceOps Load Face Shape Keys operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Load_Face_Shape_Keys_Operator = dynamic_import(
    "mpfb.ui.operations.faceops.operators.loadfaceshapekeys",
    "MPFB_OT_Load_Face_Shape_Keys_Operator"
)
FACEOPS_PROPERTIES = dynamic_import("mpfb.ui.operations.faceops.faceopspanel", "FACEOPS_PROPERTIES")


def test_load_face_shape_keys_is_registered():
    assert bpy.ops.mpfb.load_face_shape_keys is not None
    assert MPFB_OT_Load_Face_Shape_Keys_Operator is not None


def test_load_face_shape_keys_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Load_Face_Shape_Keys_Operator.poll(bpy.context)


def test_load_face_shape_keys_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Load_Face_Shape_Keys_Operator.poll(bpy.context)


# TODO: Can't assume the required asset packs are available for unit testing

