import bpy, os

from mpfb.services.locationservice import LocationService

def test_locationservice_exists():
    assert LocationService is not None, "LocationService can be imported"
    
def test_mpfb_root():
    assert os.path.exists(LocationService.get_mpfb_root()), "MPFB root directory exists"
    assert os.path.exists(LocationService.get_mpfb_root("data")), "MPFB root directory contains a data subdir"
    