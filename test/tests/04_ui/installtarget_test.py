import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.ui.assetlibrary.operators import MPFB_OT_Install_Target_Operator

class MockSelf:
    filepath = ""
    def report(self, reporttype, reportmessage):
        rep = next(iter(reporttype))
        print(str(rep) + " -- " + str(reportmessage))
        if rep == 'ERROR':
            raise ValueError(reportmessage)

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
    mockself = MockSelf()    
    mockself.filepath = target
    MPFB_OT_Install_Target_Operator.execute(mockself, bpy.context)
    assert os.path.exists(dest)
    os.remove(dest)
    assert not os.path.exists(dest)
    