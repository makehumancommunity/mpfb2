"""Tests for the Model PruneHuman operator."""

import bpy
from ... import dynamic_import, ObjectService
from .._helpers import HumanFixture

MPFB_OT_PruneHumanOperator = dynamic_import(
    "mpfb.ui.model.operators.prunehuman",
    "MPFB_OT_PruneHumanOperator"
)


def test_prune_human_is_registered():
    assert bpy.ops.mpfb.prune_human is not None
    assert MPFB_OT_PruneHumanOperator is not None


def test_prune_human_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_PruneHumanOperator.poll(bpy.context)


def test_prune_human_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_PruneHumanOperator.poll(bpy.context)
