import bpy
import pytest

# The order the top level panels are supposed to appear in, top to bottom. Every top level panel in
# the 3d view sidebar must be listed here with an explicit bl_order, so that no panel ends up in a
# position which just happens to fall out of the order the ui modules were imported in.
EXPECTED_PANEL_ORDER = {
    "MPFB_PT_Start_Here_Panel": 0,
    "MPFB_PT_New_Panel": 10,
    "MPFB_PT_Model_Panel": 20,
    "MPFB_PT_Rig_Panel": 30,
    "MPFB_PT_Assets_Panel": 40,
    "MPFB_PT_Presets_Panel": 50,
    "MPFB_PT_Operations_Panel": 60,
    "MPFB_PT_Create_Panel": 70,
    "MPFB_PT_Hair_Editor_Panel": 80,
    "MPFB_PT_Developer_Panel": 90,
    "MPFB_PT_System_Panel": 100
    }

# The first five positions are the ones a new user needs, in the order they need them. These are
# fixed, unlike the rest of the list which is a judgement call.
FIXED_PANELS = [
    "MPFB_PT_Start_Here_Panel",
    "MPFB_PT_New_Panel",
    "MPFB_PT_Model_Panel",
    "MPFB_PT_Rig_Panel",
    "MPFB_PT_Assets_Panel"
    ]

def _toplevel_sidebar_panels():
    """Find all registered MPFB panels which are drawn at the top level of the 3d view sidebar."""
    panels = dict()
    for name in dir(bpy.types):
        if not name.startswith("MPFB_PT_"):
            continue
        panel = getattr(bpy.types, name)
        if not isinstance(panel, type) or not issubclass(panel, bpy.types.Panel):
            continue
        if getattr(panel, "bl_space_type", None) != "VIEW_3D":
            continue
        if getattr(panel, "bl_region_type", None) != "UI":
            continue
        # Note that bl_parent_id exists on every registered panel, defaulting to an empty string,
        # so it has to be checked for truthiness rather than with hasattr
        if getattr(panel, "bl_parent_id", ""):
            continue
        panels[name] = getattr(panel, "bl_order", 0)
    return panels

def test_all_toplevel_panels_have_a_declared_order():
    found = _toplevel_sidebar_panels()
    assert found == EXPECTED_PANEL_ORDER, \
        "The set of top level sidebar panels has changed. If you added or removed a panel, update " \
        "EXPECTED_PANEL_ORDER in this test and give the new panel an explicit bl_order."

def test_fixed_panels_are_in_the_required_sequence():
    found = _toplevel_sidebar_panels()
    orders = []
    for name in FIXED_PANELS:
        assert name in found, name + " is not a registered top level sidebar panel"
        orders.append(found[name])
    assert orders == sorted(orders)
    assert len(set(orders)) == len(orders), "The first five panels must have distinct bl_order values"

def test_nothing_else_comes_before_apply_assets():
    found = _toplevel_sidebar_panels()
    limit = found["MPFB_PT_Assets_Panel"]
    for name, order in found.items():
        if name in FIXED_PANELS:
            continue
        assert order > limit, name + " must not be ordered before \"Apply assets\""

def test_start_here_claims_the_first_position():
    assert _toplevel_sidebar_panels()["MPFB_PT_Start_Here_Panel"] == 0

def test_randomize_subpanels_keep_their_own_order():
    """The randomize subpanels use bl_order 1-10 among themselves. Those are ordered within their
    parent and must not be confused with the top level order."""
    panel = bpy.types.MPFB_PT_Randomize_Panel
    assert panel.bl_parent_id == "MPFB_PT_New_Panel"
