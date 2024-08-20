import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.ui.makeskin.makeskinpanel import MAKESKIN_PROPERTIES
from mpfb.ui.makeskin.operators import MPFB_OT_CreateMaterialOperator


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

