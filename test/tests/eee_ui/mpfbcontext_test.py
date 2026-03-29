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
