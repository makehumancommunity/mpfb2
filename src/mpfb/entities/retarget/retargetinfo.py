from mpfb.services.logservice import LogService
from mpfb.services.rigservice import RigService

_LOG = LogService.get_logger("retarget.retargetinfo")
_LOG.set_level(LogService.DEBUG)

class RetargetInfo:

    def __init__(self):
        pass

    def get_body_length_chain(self):
        return []

    def get_arm_length_chain(self):
        return []

    def get_leg_length_chain(self):
        return []

    def get_root_bone(self):
        return None

    def get_left_hand_bone(self):
        return None

    def get_right_hand_bone(self):
        return None

    def get_left_foot_bone(self):
        return None

    def get_right_foot_bone(self):
        return None

    def adjust_root(self): # As absolute xyz world coord
        return [0.0, 0.0, 0.0]