import os, hashlib
from mpfb.services.locationservice import LocationService

def test_3dobjs_dir_exists():
    """3dobjs dir"""
    assert os.path.exists(LocationService.get_mpfb_data("3dobjs"))

def test_baseobj():
    """base.obj"""
    objsdir = LocationService.get_mpfb_data("3dobjs")
    baseobj = os.path.join(objsdir, "base.obj")
    assert os.path.exists(baseobj)
    with open(baseobj, "r") as bobj:
        bobjstr = bobj.read()
    filesum = hashlib.md5(bobjstr.encode('utf-8')).hexdigest()
    assert filesum == "89848fdd9706aa0c9d33b12361a9e407"
