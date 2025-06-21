import pytest, os

tests = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests"))

if "TEST_MODULE" in os.environ:
    tests = os.path.abspath(os.path.join(tests, "..", os.environ['TEST_MODULE']))
    print("TEST_MODULE is set: " + tests)

retcode = pytest.main(["-v", "--capture=tee-sys", "--cov-report", "html:coverage", "--cov", "-x", tests])
if retcode:
    print("Unit tests have finished with error code " + str(retcode) + ". See console output for results.")
else:
    print("Unit tests have finished without error. See console output for results.")

