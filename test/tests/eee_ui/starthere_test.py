import bpy
import pytest
from .. import dynamic_import
from ._helpers import MockOperatorBase

MPFB_OT_Dismiss_Start_Here_Operator = dynamic_import("mpfb.ui.start_here.operators.dismissstarthere", "MPFB_OT_Dismiss_Start_Here_Operator")
get_preference = dynamic_import("mpfb", "get_preference")
set_preference = dynamic_import("mpfb", "set_preference")

def test_operators_exist():
    """Operators are not none"""
    assert bpy.ops.mpfb.dismiss_start_here is not None

def test_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Start_Here_Panel")

def test_panel_is_first_and_open():
    panel = bpy.types.MPFB_PT_Start_Here_Panel
    assert panel.bl_order == 0
    assert "DEFAULT_CLOSED" not in panel.bl_options

def test_preference_exists():
    assert get_preference("mpfb_show_start_here") is not None

def test_poll_is_true_by_default():
    try:
        set_preference("mpfb_show_start_here", True)
        assert bpy.types.MPFB_PT_Start_Here_Panel.poll(bpy.context)
    finally:
        set_preference("mpfb_show_start_here", True)

def test_dismiss_hides_panel():
    try:
        set_preference("mpfb_show_start_here", True)
        mockself = MockOperatorBase()
        MPFB_OT_Dismiss_Start_Here_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()
        assert get_preference("mpfb_show_start_here") is False
        assert not bpy.types.MPFB_PT_Start_Here_Panel.poll(bpy.context)
    finally:
        # This preference is global for the blender installation, so it must not leak
        set_preference("mpfb_show_start_here", True)
    assert bpy.types.MPFB_PT_Start_Here_Panel.poll(bpy.context)
