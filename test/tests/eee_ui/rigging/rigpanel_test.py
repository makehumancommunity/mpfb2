"""Tests for the top-level Rig panel registration."""

import bpy
from ... import dynamic_import, ObjectService
from .._helpers import HumanFixture, HumanWithRigFixture

MPFB_PT_Rig_Panel = dynamic_import("mpfb.ui.rigging.rigpanel", "MPFB_PT_Rig_Panel")


def test_rig_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Rig_Panel")
    assert MPFB_PT_Rig_Panel is not None


def test_rig_panel_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_PT_Rig_Panel.poll(bpy.context)


def test_rig_panel_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_PT_Rig_Panel.poll(bpy.context)


def test_rig_panel_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        assert MPFB_PT_Rig_Panel.poll(bpy.context)
