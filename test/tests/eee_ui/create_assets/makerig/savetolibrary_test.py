"""Tests for the MakeRig SaveToLibrary operator."""

import bpy
import os
from .... import dynamic_import, ObjectService, LocationService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_Save_Rig_To_Library_Operator = dynamic_import("mpfb.ui.create_assets.makerig.operators.savetolibrary", "MPFB_OT_Save_Rig_To_Library_Operator")
MakeRigProperties = dynamic_import("mpfb.ui.create_assets.makerig", "MakeRigProperties")


def test_save_rig_to_library_is_registered():
    assert bpy.ops.mpfb.save_rig_to_library is not None
    assert MPFB_OT_Save_Rig_To_Library_Operator is not None


def test_save_rig_to_library_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Save_Rig_To_Library_Operator.poll(bpy.context)


def test_save_rig_to_library_poll_true_with_armature():
    with HumanWithRigFixture() as fixture:
        assert MPFB_OT_Save_Rig_To_Library_Operator.poll(bpy.context)


def test_save_rig_to_library_errors_invalid_rig_name():
    with HumanWithRigFixture() as fixture:
        scene = bpy.context.scene
        MakeRigProperties.set_value("library_rig_name", "my rig", entity_reference=scene)
        MakeRigProperties.set_value("library_identifying_bones", "root", entity_reference=scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_Save_Rig_To_Library_Operator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "letters")


def test_save_rig_to_library_errors_empty_identifying_bones():
    with HumanWithRigFixture() as fixture:
        scene = bpy.context.scene
        MakeRigProperties.set_value("library_rig_name", "test_rig", entity_reference=scene)
        MakeRigProperties.set_value("library_identifying_bones", "", entity_reference=scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_Save_Rig_To_Library_Operator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "identifying bone")


def test_save_rig_to_library_errors_nonexistent_bone():
    with HumanWithRigFixture() as fixture:
        scene = bpy.context.scene
        MakeRigProperties.set_value("library_rig_name", "test_rig", entity_reference=scene)
        MakeRigProperties.set_value("library_identifying_bones", "nonexistent_bone_xyz", entity_reference=scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_Save_Rig_To_Library_Operator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "not found")
