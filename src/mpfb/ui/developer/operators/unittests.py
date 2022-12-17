"""Functionality for running unit tests. See README in the test directory before using this."""

from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("developer.unittests")

class MPFB_OT_Unit_Tests_Operator(bpy.types.Operator):
    """Run unit tests. See console output for results"""
    bl_idname = "mpfb.unit_tests"
    bl_label = "Run unit tests"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()
        import pytest
        tests = LocationService.get_mpfb_test("tests")
        retcode = pytest.main(["-x", tests])
        if retcode:
            self.report({'ERROR'}, "Unit tests have finished with error code " + str(retcode) + ". See console output for results.")
        else:
            self.report({'INFO'}, "Unit tests have finished without error. See console output for results.")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Unit_Tests_Operator)
