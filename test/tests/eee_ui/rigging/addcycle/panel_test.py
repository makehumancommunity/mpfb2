"""Tests for the Add Walk Cycle panel registration."""

import bpy
from .... import dynamic_import

MPFB_PT_Add_Cycle_Panel = dynamic_import(
    "mpfb.ui.rigging.addcycle.addcyclepanel", "MPFB_PT_Add_Cycle_Panel"
)


def test_add_cycle_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Add_Cycle_Panel")
    assert MPFB_PT_Add_Cycle_Panel is not None
