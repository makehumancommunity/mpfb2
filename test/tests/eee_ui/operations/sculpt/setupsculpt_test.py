"""Tests for the Sculpt Setup Sculpt operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Setup_Sculpt_Operator = dynamic_import(
    "mpfb.ui.operations.sculpt.operators.setupsculpt",
    "MPFB_OT_Setup_Sculpt_Operator"
)
SCULPT_PROPERTIES = dynamic_import("mpfb.ui.operations.sculpt.sculptpanel", "SCULPT_PROPERTIES")


def test_setup_sculpt_is_registered():
    assert bpy.ops.mpfb.setup_sculpt is not None
    assert MPFB_OT_Setup_Sculpt_Operator is not None


def test_setup_sculpt_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Setup_Sculpt_Operator.poll(bpy.context)


def test_setup_sculpt_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Setup_Sculpt_Operator.poll(bpy.context)


def test_setup_sculpt_executes_with_basemesh_origin_strategy():
    with HumanFixture() as fixture:
        # Use ORIGIN strategy — safest: no copies are made, no armature needed
        SCULPT_PROPERTIES.set_value("sculpt_strategy", "ORIGIN", entity_reference=bpy.context.scene)
        # Operator uses self._handle_bm() etc — requires real operator instance via bpy.ops
        result = bpy.ops.mpfb.setup_sculpt()
        assert result == {'FINISHED'}
