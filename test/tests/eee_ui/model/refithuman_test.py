"""Tests for the Model RefitHuman operator."""

import bpy
from ... import dynamic_import, ObjectService
from .._helpers import HumanFixture, HumanWithRigFixture

MPFB_OT_RefitHumanOperator = dynamic_import(
    "mpfb.ui.model.operators.refithuman",
    "MPFB_OT_RefitHumanOperator"
)


def test_refit_human_is_registered():
    assert bpy.ops.mpfb.refit_human is not None
    assert MPFB_OT_RefitHumanOperator is not None


def test_refit_human_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_RefitHumanOperator.poll(bpy.context)


def test_refit_human_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_RefitHumanOperator.poll(bpy.context)


def test_refit_human_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        assert MPFB_OT_RefitHumanOperator.poll(bpy.context)
