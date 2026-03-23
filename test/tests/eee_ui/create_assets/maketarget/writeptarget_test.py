"""Tests for the MakeTarget WritePtarget operator."""

import bpy
import tempfile
import os
from .... import dynamic_import, ObjectService, TargetService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_WritePtargetOperator = dynamic_import(
    "mpfb.ui.create_assets.maketarget.operators.writeptarget", "MPFB_OT_WritePtargetOperator")
GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")


def _create_proxy_mesh():
    """Create a cube with type=Clothes and a PrimaryTarget shape key."""
    bpy.ops.mesh.primitive_cube_add()
    proxy = bpy.context.active_object
    GeneralObjectProperties.set_value("object_type", "Clothes", entity_reference=proxy)
    TargetService.create_shape_key(proxy, "PrimaryTarget")
    ObjectService.activate_blender_object(proxy)
    return proxy


def test_write_ptarget_is_registered():
    assert bpy.ops.mpfb.write_maketarget_ptarget is not None
    assert MPFB_OT_WritePtargetOperator is not None


def test_write_ptarget_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_WritePtargetOperator.poll(bpy.context)


def test_write_ptarget_poll_false_with_basemesh():
    with HumanFixture() as fixture:
        # Basemesh is excluded by poll
        assert not MPFB_OT_WritePtargetOperator.poll(bpy.context)


def test_write_ptarget_poll_true_with_proxy_mesh():
    proxy = _create_proxy_mesh()
    try:
        assert MPFB_OT_WritePtargetOperator.poll(bpy.context)
    finally:
        ObjectService.delete_object(proxy)


def test_write_ptarget_execute_writes_file():
    proxy = _create_proxy_mesh()
    fd, tmp_path = tempfile.mkstemp(suffix=".ptarget")
    os.close(fd)
    try:
        mockself = MockOperatorBase(filepath=tmp_path)
        result = MPFB_OT_WritePtargetOperator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
        assert os.path.exists(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        ObjectService.delete_object(proxy)
