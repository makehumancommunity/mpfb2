import bpy, os
from pytest import approx
from .. import ObjectService
from .. import dynamic_import
MAKESKIN_PROPERTIES = dynamic_import("mpfb.ui.makeskin.makeskinpanel", "MAKESKIN_PROPERTIES")
MPFB_OT_CreateMaterialOperator = dynamic_import("mpfb.ui.makeskin.operators", "MPFB_OT_CreateMaterialOperator")


class MockSelf:
    filepath = ""

    def report(self, reporttype, reportmessage):
        rep = next(iter(reporttype))
        print(str(rep) + " -- " + str(reportmessage))
        if rep == 'ERROR':
            raise ValueError(reportmessage)


def test_operators_exist():
    """Operators are not none"""
    assert bpy.ops.mpfb.create_makeskin_material is not None
    assert MPFB_OT_CreateMaterialOperator is not None

