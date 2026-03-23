"""Tests for the Add Rig Generate Rigify Rig operator.

The poll requires a rigify meta-rig to be active. In the test environment we only verify
registration and that the poll returns False when no suitable object is present.
"""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import HumanWithRigFixture

MPFB_OT_GenerateRigifyRigOperator = dynamic_import(
    "mpfb.ui.rigging.addrig.operators.generaterigifyrig",
    "MPFB_OT_GenerateRigifyRigOperator",
)


def test_generate_rigify_rig_is_registered():
    assert bpy.ops.mpfb.generate_rigify_rig is not None
    assert MPFB_OT_GenerateRigifyRigOperator is not None


def test_generate_rigify_rig_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_GenerateRigifyRigOperator.poll(bpy.context)


def test_generate_rigify_rig_poll_false_with_standard_rig():
    # A standard (non-rigify) rig should not satisfy the poll
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        assert not MPFB_OT_GenerateRigifyRigOperator.poll(bpy.context)
