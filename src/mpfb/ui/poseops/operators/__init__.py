from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("poseoperators.init")
_LOG.trace("initializing pose operators")

from .apply_pose import MPFB_OT_Apply_Pose_Operator

__all__ = [
    "MPFB_OT_Apply_Pose_Operator"
    ]
