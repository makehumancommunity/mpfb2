"""Tests for the MakeTarget ImportTarget operator."""

import bpy
import tempfile
import os
from .... import dynamic_import, ObjectService, TargetService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_ImportTargetOperator = dynamic_import(
    "mpfb.ui.create_assets.maketarget.operators.importtarget", "MPFB_OT_ImportTargetOperator")


def test_import_target_is_registered():
    assert bpy.ops.mpfb.import_maketarget_target is not None
    assert MPFB_OT_ImportTargetOperator is not None


def test_import_target_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_ImportTargetOperator.poll(bpy.context)


def test_import_target_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        # No PrimaryTarget exists yet → poll is True
        assert MPFB_OT_ImportTargetOperator.poll(bpy.context)


def test_import_target_execute_imports_target():
    with HumanFixture() as fixture:
        fd, tmp_path = tempfile.mkstemp(suffix=".target")
        os.close(fd)
        try:
            # Empty .target = no vertex displacements, still valid
            with open(tmp_path, 'w') as f:
                f.write("")
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_ImportTargetOperator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()
            assert TargetService.has_target(fixture.basemesh, "PrimaryTarget")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
