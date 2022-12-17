import pytest
from mpfb.services.locationservice import LocationService

tests = LocationService.get_mpfb_test("tests")
retcode = pytest.main(["-x", tests])
if retcode:
    print("Unit tests have finished with error code " + str(retcode) + ". See console output for results.")
else:
    print("Unit tests have finished without error. See console output for results.")

