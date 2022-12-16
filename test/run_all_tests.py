import bpy
import pytest

from mpfb.services.locationservice import LocationService

tests = LocationService.get_mpfb_test("tests")

retcode = pytest.main(["-x", tests])

