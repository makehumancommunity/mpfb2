from .retargetinfo import RetargetInfo
from mpfb.services.logservice import LogService
from mpfb.services.rigservice import RigService

_LOG = LogService.get_logger("retarget.default")
_LOG.set_level(LogService.DEBUG)

class Default(RetargetInfo):
    
    def __init__(self):
        RetargetInfo.__init__(self)
        
    def get_body_length_chain(self):
        return ["lowerleg02.L", "lowerleg01.L", "upperleg02.L", "upperleg01.L", "spine05", "spine04", "spine03", "spine02", "spine01", "neck01", "neck02", "head"]

    def get_arm_length_chain(self):
        return ["upperarm01.L", "upperarm02.L", "lowerarm01.L", "lowerarm02.L"]

    def get_leg_length_chain(self):
        return ["lowerleg02.L", "lowerleg01.L", "upperleg02.L", "upperleg01.L"]
    
    def get_root_bone(self):
        return "root"

    def get_left_hand_bone(self):
        return "left_hand_ik"
    
    def get_right_hand_bone(self):
        return "right_hand_ik"
    
    def get_left_foot_bone(self):
        return "left_foot_ik"
    
    def get_right_foot_bone(self):
        return "right_foot_ik"
