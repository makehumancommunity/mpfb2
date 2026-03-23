import bpy, os
from pytest import approx
from .. import ObjectService
from .. import LocationService
from .. import dynamic_import
from ._helpers import MockOperatorBase
MPFB_OT_Install_Target_Operator = dynamic_import("mpfb.ui.assetlibrary.operators", "MPFB_OT_Install_Target_Operator")


def test_operators_exist():
    """Operators are not none"""
    assert bpy.ops.mpfb.install_target is not None
    assert MPFB_OT_Install_Target_Operator is not None


def test_install_target():
    testdata = LocationService.get_mpfb_test("testdata")
    target = os.path.join(testdata, "autotest.target")
    custom = LocationService.get_user_data("custom")
    dest = os.path.join(custom, os.path.basename(target))
    assert not os.path.exists(dest)
    mockself = MockOperatorBase(filepath=target)
    MPFB_OT_Install_Target_Operator.execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    assert os.path.exists(dest)
    os.remove(dest)
    assert not os.path.exists(dest)
