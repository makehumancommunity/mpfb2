"""Tests for the HumanPresets OverwritePresets operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import HumanFixture

MPFB_OT_Overwrite_Human_Presets_Operator = dynamic_import(
    "mpfb.ui.presets.humanpresets.operators.overwritepresets",
    "MPFB_OT_Overwrite_Human_Presets_Operator"
)


def test_overwrite_human_presets_is_registered():
    assert bpy.ops.mpfb.overwrite_human_presets is not None
    assert MPFB_OT_Overwrite_Human_Presets_Operator is not None


def test_overwrite_human_presets_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Overwrite_Human_Presets_Operator.poll(bpy.context)


def test_overwrite_human_presets_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Overwrite_Human_Presets_Operator.poll(bpy.context)
