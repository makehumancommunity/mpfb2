"""Tests for the MakeWeight TruncateWeights operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_TruncateWeightsOperator = dynamic_import("mpfb.ui.create_assets.makeweight.operators.truncateweights", "MPFB_OT_TruncateWeightsOperator")
MAKEWEIGHT_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeweight.makeweightpanel", "MAKEWEIGHT_PROPERTIES")


def test_truncate_weights_is_registered():
    assert bpy.ops.mpfb.truncate_weights is not None
    assert MPFB_OT_TruncateWeightsOperator is not None


def test_truncate_weights_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_TruncateWeightsOperator.poll(bpy.context)


def test_truncate_weights_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_TruncateWeightsOperator.poll(bpy.context)


def test_truncate_weights_executes_successfully():
    with HumanFixture() as fixture:
        # Get the first vertex group name that isn't a joint
        group_name = None
        for group in fixture.basemesh.vertex_groups:
            if not group.name.startswith("joint-"):
                group_name = group.name
                break
        if group_name is None:
            if fixture.basemesh.vertex_groups:
                group_name = fixture.basemesh.vertex_groups[0].name
        if group_name is None:
            return  # No vertex groups, skip
        MAKEWEIGHT_PROPERTIES.set_value("vertex_group", group_name, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_TruncateWeightsOperator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
