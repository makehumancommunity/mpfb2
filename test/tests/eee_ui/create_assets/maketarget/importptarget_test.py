"""Tests for the MakeTarget ImportPtarget operator."""

import bpy
import tempfile
import os
from .... import dynamic_import, ObjectService, TargetService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_ImportPtargetOperator = dynamic_import(
    "mpfb.ui.create_assets.maketarget.operators.importptarget", "MPFB_OT_ImportPtargetOperator")


def test_import_ptarget_is_registered():
    assert bpy.ops.mpfb.import_maketarget_ptarget is not None
    assert MPFB_OT_ImportPtargetOperator is not None


def test_import_ptarget_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_ImportPtargetOperator.poll(bpy.context)


def test_import_ptarget_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        # Basemesh is not a Skeleton and has no PrimaryTarget → poll is True
        assert MPFB_OT_ImportPtargetOperator.poll(bpy.context)


def test_import_ptarget_execute_imports_target():
    with HumanFixture() as fixture:
        fd, tmp_path = tempfile.mkstemp(suffix=".ptarget")
        os.close(fd)
        try:
            # Empty .ptarget = no vertex displacements, still valid
            with open(tmp_path, 'w') as f:
                f.write("")
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_ImportPtargetOperator.execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()
            assert TargetService.has_target(fixture.basemesh, "PrimaryTarget")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
