"""Tests for the MakeSkin CreateMaterial operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MAKESKIN_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeskin.makeskinpanel", "MAKESKIN_PROPERTIES")
MPFB_OT_CreateMaterialOperator = dynamic_import("mpfb.ui.create_assets.makeskin.operators", "MPFB_OT_CreateMaterialOperator")


def test_create_material_is_registered():
    assert bpy.ops.mpfb.create_makeskin_material is not None
    assert MPFB_OT_CreateMaterialOperator is not None


def test_create_material_poll_false_with_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_CreateMaterialOperator.poll(bpy.context)


def test_create_material_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_CreateMaterialOperator.poll(bpy.context)


def test_create_material_executes_successfully():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_CreateMaterialOperator.execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()
        assert result == {'FINISHED'}
        MaterialService = dynamic_import("mpfb.services.materialservice", "MaterialService")
        assert MaterialService.has_materials(fixture.basemesh)


def test_create_material_errors_when_specular_and_roughness_both_set():
    with HumanFixture() as fixture:
        MAKESKIN_PROPERTIES.set_value("create_specularmap", True, entity_reference=bpy.context.scene)
        MAKESKIN_PROPERTIES.set_value("create_roughnessmap", True, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_CreateMaterialOperator.execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', 'specular')
        MAKESKIN_PROPERTIES.set_value("create_specularmap", False, entity_reference=bpy.context.scene)
        MAKESKIN_PROPERTIES.set_value("create_roughnessmap", False, entity_reference=bpy.context.scene)
