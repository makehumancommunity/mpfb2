"""Tests for the MakeRig SaveRig operator."""

import bpy
import tempfile
import os
import json
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_Save_Rig_Operator = dynamic_import("mpfb.ui.create_assets.makerig.operators.saverig", "MPFB_OT_Save_Rig_Operator")


def test_save_rig_is_registered():
    assert bpy.ops.mpfb.save_rig is not None
    assert MPFB_OT_Save_Rig_Operator is not None


def test_save_rig_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Save_Rig_Operator.poll(bpy.context)


def test_save_rig_poll_true_with_armature():
    with HumanWithRigFixture() as fixture:
        # fixture activates the rig
        assert MPFB_OT_Save_Rig_Operator.poll(bpy.context)


def test_save_rig_executes_successfully():
    with HumanWithRigFixture() as fixture:
        fd, tmp_path = tempfile.mkstemp(suffix=".mpfbskel")
        os.close(fd)
        try:
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_Save_Rig_Operator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            assert os.path.getsize(tmp_path) > 0
            # Verify it's valid JSON
            with open(tmp_path, 'r') as f:
                data = json.load(f)
            assert isinstance(data, dict)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
