"""Tests for the MakeWeight ImportWeights operator."""

import bpy
import tempfile
import os
import json
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_ImportWeightsOperator = dynamic_import(
    "mpfb.ui.create_assets.makeweight.operators.importweights", "MPFB_OT_ImportWeightsOperator")


def test_import_makeweight_weight_is_registered():
    assert bpy.ops.mpfb.import_makeweight_weight is not None
    assert MPFB_OT_ImportWeightsOperator is not None


def test_import_makeweight_weight_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_ImportWeightsOperator.poll(bpy.context)


def test_import_makeweight_weight_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_ImportWeightsOperator.poll(bpy.context)


def test_import_makeweight_weight_execute_reads_file():
    with HumanFixture() as fixture:
        fd, tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            with open(tmp_path, 'w') as f:
                json.dump({}, f)
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_ImportWeightsOperator.hardened_execute(mockself, bpy.context)
            # Stub operator just reads file and reports success
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
