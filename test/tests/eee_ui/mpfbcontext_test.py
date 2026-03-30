import bpy
from .. import dynamic_import, ObjectService
from ._helpers import HumanWithRigAndClothesFixture

MpfbContext = dynamic_import("mpfb.ui.mpfbcontext", "MpfbContext")

def test_create_mpfb_context():
    ObjectService.deselect_and_deactivate_all()
    with HumanWithRigAndClothesFixture() as fixture:
        ctx = MpfbContext()
        assert ctx.active_object is not None
        assert ctx.focus_object is not None
        assert ObjectService.object_is_basemesh(ctx.focus_object)

def test_populate_dict():
    ObjectService.deselect_and_deactivate_all()
    with HumanWithRigAndClothesFixture() as fixture:
        ctx = MpfbContext()
        target = {}
        ctx.populate_dict(target, ["active_object", "scene", "context"])
        assert target["active_object"] == ctx.active_object
        assert target["scene"] == ctx.scene
        assert target["context"] == ctx.context

def test_populate_dict_noop_when_no_keys():
    ObjectService.deselect_and_deactivate_all()
    with HumanWithRigAndClothesFixture() as fixture:
        ctx = MpfbContext()
        target = {"active_object": "PLACEHOLDER"}
        ctx.populate_dict(target)
        assert target["active_object"] == "PLACEHOLDER"
