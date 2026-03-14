"""Tests for the MakePose SaveAnimation operator."""

import bpy
import pytest
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_Save_Animation_Operator = dynamic_import("mpfb.ui.create_assets.makepose.operators.saveanimation", "MPFB_OT_Save_Animation_Operator")


def test_save_animation_is_registered():
    assert bpy.ops.mpfb.save_animation is not None
    assert MPFB_OT_Save_Animation_Operator is not None


def test_save_animation_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Save_Animation_Operator.poll(bpy.context)


def test_save_animation_poll_true_with_armature():
    with HumanWithRigFixture() as fixture:
        assert MPFB_OT_Save_Animation_Operator.poll(bpy.context)
