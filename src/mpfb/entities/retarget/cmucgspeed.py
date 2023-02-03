from .retargetinfo import RetargetInfo
from mpfb.services.logservice import LogService
from mpfb.services.rigservice import RigService

_LOG = LogService.get_logger("retarget.cmucgspeed")
_LOG.set_level(LogService.DEBUG)

class CmuCgspeed(RetargetInfo):

    def __init__(self):
        RetargetInfo.__init__(self)

    def get_body_length_chain(self):
        return ["rShin", "rThigh", "hip", "abdomen", "abdomen", "chest", "neck", "head"] # Abdomen twice, since there's a gap in the rig

    def get_arm_length_chain(self):
        return ["rShldr", "rForeArm"]

    def get_leg_length_chain(self):
        return ["rShin", "rThig"]

    def get_root_bone(self):
        return "hip"

    def get_left_hand_bone(self):
        return "lHand"

    def get_right_hand_bone(self):
        return "rHand"

    def get_left_foot_bone(self):
        return "lFoot"

    def get_right_foot_bone(self):
        return "rFoot"

    def adjust_root(self): # As absolute xyz world coord
        return [0.0, -0.1, -0.1]