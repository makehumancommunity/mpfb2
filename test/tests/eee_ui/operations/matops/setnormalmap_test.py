"""Tests for the MatOps Set Normal Map operator."""

import bpy
import os
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, BasemeshWithV2SkinFixture

MPFB_OT_Set_Normalmap_Operator = dynamic_import(
    "mpfb.ui.operations.matops.operators.setnormalmap",
    "MPFB_OT_Set_Normalmap_Operator"
)

_TEST_PNG = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "testdata", "materials", "diffuseTexture.png"
))


def test_set_normalmap_is_registered():
    assert bpy.ops.mpfb.set_normalmap is not None
    assert MPFB_OT_Set_Normalmap_Operator is not None


def test_set_normalmap_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Set_Normalmap_Operator.poll(bpy.context)


def test_set_normalmap_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Set_Normalmap_Operator.poll(bpy.context)


def test_set_normalmap_errors_without_material():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Set_Normalmap_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "needs to have a material")


def test_set_normalmap_executes_with_v2_skin():
    with BasemeshWithV2SkinFixture() as fixture:
        mockself = MockOperatorBase(filepath=_TEST_PNG)
        result = MPFB_OT_Set_Normalmap_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
