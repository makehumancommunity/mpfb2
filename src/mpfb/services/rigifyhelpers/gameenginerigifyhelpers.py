"""This module contains the gameengine rig's implementation of the rigify helpers class"""


from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("rigifyhelpers.gameenginerigifyhelpers")

from mpfb.services.rigifyhelpers.rigifyhelpers import RigifyHelpers

class GameEngineRigifyHelpers(RigifyHelpers):

    """The rig specific implementation of rigify helpers matching the Game engine rig."""

    def __init__(self, settings):
        """Get a new instance of the class. You should not call this directly. Instead, use the get_instance()
        method in the abstract base class."""

        _LOG.debug("Constructing GameEngineRigifyHelpers object")
        RigifyHelpers.__init__(self, settings)

    def get_list_of_spine_bones(self):
        _LOG.enter()
        bones = ["pelvis"]
        for i in range(3):
            bones.append("spine_0" + str(i+1))
        return bones

    def get_list_of_arm_bones(self, left_side=True):
        _LOG.enter()
        bone_names = ["upperarm", "lowerarm", "hand"]
        bones = []
        if left_side:
            side = "_l"
        else:
            side = "_r"
        for bone_name in bone_names:
            bones.append(bone_name + side)
        return bones

    def get_list_of_leg_bones(self, left_side=True):
        _LOG.enter()
        bone_names = ["thigh", "calf", "foot", "ball"]
        bones = []
        if left_side:
            side = "_l"
        else:
            side = "_r"
        for bone_name in bone_names:
            bones.append(bone_name + side)
        return bones

    def get_list_of_shoulder_bones(self, left_side=True):
        _LOG.enter()
        bone_names = ["clavicle"]
        bones = []
        if left_side:
            side = "_l"
        else:
            side = "_r"
        for bone_name in bone_names:
            bones.append(bone_name + side)
        return bones

    def get_list_of_head_bones(self):
        _LOG.enter()
        return ["neck_01", "head"]

    def get_list_of_finger_bones(self, finger_number, left_side=True):
        finger_names = ["thumb", "index", "middle", "ring", "pinky"]
        if left_side:
            side = "_l"
        else:
            side = "_r"
        finger_name = finger_names[finger_number]
        bones = []
        for i in range(3):
            bones.append(finger_name + "_0" + str(i+1) + side)
        return bones
