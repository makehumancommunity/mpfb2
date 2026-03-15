"""Tests for the AnimOps Map Mixamo operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, TwoMixamoArmaturesFixture

MPFB_OT_Map_Mixamo_Operator = dynamic_import(
    "mpfb.ui.operations.animops.operators.mapmixamo",
    "MPFB_OT_Map_Mixamo_Operator"
)


def test_map_mixamo_is_registered():
    assert bpy.ops.mpfb.map_mixamo is not None
    assert MPFB_OT_Map_Mixamo_Operator is not None

# TODO: Properly test map mixamo (would need some test data)


