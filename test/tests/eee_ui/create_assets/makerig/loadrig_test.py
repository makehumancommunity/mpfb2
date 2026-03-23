"""Tests for the MakeRig LoadRig operator."""

import bpy
from .... import dynamic_import, ObjectService, LocationService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Load_Rig_Operator = dynamic_import("mpfb.ui.create_assets.makerig.operators.loadrig", "MPFB_OT_Load_Rig_Operator")
MakeRigProperties = dynamic_import("mpfb.ui.create_assets.makerig", "MakeRigProperties")


def test_load_rig_is_registered():
    assert bpy.ops.mpfb.load_rig is not None
    assert MPFB_OT_Load_Rig_Operator is not None


def test_load_rig_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Load_Rig_Operator.poll(bpy.context)


def test_load_rig_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        # Ensure rig_subrig is False (default)
        MakeRigProperties.set_value("rig_subrig", False, entity_reference=bpy.context.scene)
        assert MPFB_OT_Load_Rig_Operator.poll(bpy.context)


def test_load_rig_executes_successfully():
    with HumanFixture() as fixture:
        MakeRigProperties.set_value("rig_subrig", False, entity_reference=bpy.context.scene)
        MakeRigProperties.set_value("rig_parent", True, entity_reference=bpy.context.scene)
        rig_path = LocationService.get_mpfb_data("rigs/standard/rig.default.json")
        mockself = MockOperatorBase(filepath=rig_path)
        result = MPFB_OT_Load_Rig_Operator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
