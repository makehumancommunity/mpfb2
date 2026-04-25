"""Tests for the MakeRig LoadWeights operator."""

import bpy
from .... import dynamic_import, ObjectService, LocationService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Load_Weights_Operator = dynamic_import("mpfb.ui.create_assets.makerig.operators.loadweights", "MPFB_OT_Load_Weights_Operator")
MakeRigProperties = dynamic_import("mpfb.ui.create_assets.makerig", "MakeRigProperties")


def test_load_weights_is_registered():
    assert bpy.ops.mpfb.load_weights is not None
    assert MPFB_OT_Load_Weights_Operator is not None


def test_load_weights_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Load_Weights_Operator.poll(bpy.context)


def test_load_weights_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Load_Weights_Operator.poll(bpy.context)


def test_load_weights_errors_without_skeleton():
    with HumanFixture() as fixture:
        weights_path = LocationService.get_mpfb_data("rigs/standard/weights.default.json")
        mockself = MockOperatorBase(filepath=weights_path)
        result = MPFB_OT_Load_Weights_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "skeleton")


def test_load_weights_executes_with_rig():
    with HumanWithRigFixture() as fixture:
        ObjectService.activate_blender_object(fixture.basemesh)
        weights_path = LocationService.get_mpfb_data("rigs/standard/weights.default.json")
        mockself = MockOperatorBase(filepath=weights_path)
        result = MPFB_OT_Load_Weights_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()


def test_load_weights_clears_bone_groups_when_flag_set():
    with HumanWithRigFixture() as fixture:
        ObjectService.activate_blender_object(fixture.basemesh)
        bone_name = fixture.rig.data.bones[0].name
        vg = fixture.basemesh.vertex_groups.new(name=bone_name)
        indices = list(range(len(fixture.basemesh.data.vertices)))
        vg.add(indices, 1.0, 'REPLACE')
        assert fixture.basemesh.vertex_groups.get(bone_name) is not None
        MakeRigProperties.set_value("clear_weights", True, entity_reference=bpy.context.scene)
        weights_path = LocationService.get_mpfb_data("rigs/standard/weights.default.json")
        mockself = MockOperatorBase(filepath=weights_path)
        result = MPFB_OT_Load_Weights_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
        vg_after = fixture.basemesh.vertex_groups.get(bone_name)
        if vg_after is not None:
            count_with_weight = sum(
                1 for v in fixture.basemesh.data.vertices
                for g in v.groups if g.group == vg_after.index and g.weight > 0.001
            )
            total = len(fixture.basemesh.data.vertices)
            assert count_with_weight < total, "After clear+reload, only bone-relevant vertices should have weight (not all)"
        MakeRigProperties.set_value("clear_weights", False, entity_reference=bpy.context.scene)


def test_load_weights_preserves_weights_by_default():
    with HumanWithRigFixture() as fixture:
        ObjectService.activate_blender_object(fixture.basemesh)
        MakeRigProperties.set_value("clear_weights", False, entity_reference=bpy.context.scene)
        weights_path = LocationService.get_mpfb_data("rigs/standard/weights.default.json")
        mockself = MockOperatorBase(filepath=weights_path)
        result = MPFB_OT_Load_Weights_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
