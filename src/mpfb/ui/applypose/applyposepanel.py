import os, bpy
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.services.rigservice import RigService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("applypose.applyposepanel")

POSES_PROPERTIES = SceneConfigSet([], prefix="POSES_")

def _populate_partials(self, context):
    _LOG.enter()
    if context.object is None or context.object.type != 'ARMATURE':
        return []
    armature_object = context.object
    rig_type = RigService.identify_rig(armature_object)
    if "default" in rig_type:
        rig_type = "default"
    mode = "_partial"

    poses_root = LocationService.get_user_data("poses")
    if not os.path.exists(poses_root):
        return []
    pose_root = os.path.join(poses_root, rig_type + mode)
    _LOG.debug("pose root", pose_root)
    if not os.path.exists(pose_root):
        return []

    line = 0
    poses = []
    items = os.listdir(pose_root)
    for item in items:
        if str(item).endswith(".json"):
            name = str(item).replace(".json", "")
            poses.append((name, name, name, line))
            line = line + 1
    poses.sort()
    return poses

def _populate_poses(self, context):
    _LOG.enter()
    if context.object is None or context.object.type != 'ARMATURE':
        return []
    armature_object = context.object
    rig_type = RigService.identify_rig(armature_object)
    if "default" in rig_type:
        rig_type = "default"
    mode = "_fk"

    for bone in armature_object.data.bones:
        if str(bone.name).endswith("_ik"):
            mode = "_ik"

    poses_root = LocationService.get_user_data("poses")
    if not os.path.exists(poses_root):
        return []
    pose_root = os.path.join(poses_root, rig_type + mode)
    _LOG.debug("pose root", pose_root)
    if not os.path.exists(pose_root):
        return []

    line = 0
    poses = []
    items = os.listdir(pose_root)
    for item in items:
        if str(item).endswith(".json"):
            name = str(item).replace(".json", "")
            poses.append((name, name, name, line))
            line = line + 1
    poses.sort()
    return poses

_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "available_poses",
    "description": "These are the poses that match the rig type and its current mode. If you don't see an expected pose here, maybe it is because you have / don't have rig helpers enabled",
    "label": "Pose",
    "default": None
}
POSES_PROPERTIES.add_property(_SETTINGS_LIST_PROP, _populate_poses)

_SETTINGS_PART_PROP = {
    "type": "enum",
    "name": "available_partials",
    "description": "These are the partial poses that match the rig type",
    "label": "Partial pose",
    "default": None
}
POSES_PROPERTIES.add_property(_SETTINGS_PART_PROP, _populate_partials)

_GLOBAL_POSES_SCANNED = False

class MPFB_PT_ApplyPosePanel(Abstract_Panel):
    bl_label = "Load pose"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Rig_Panel"

    def draw(self, context):
        _LOG.enter()

        global _GLOBAL_POSES_SCANNED
        if not _GLOBAL_POSES_SCANNED:
            _LOG.debug("Will now scan global poses")
            RigService.ensure_global_poses_are_available()
            _GLOBAL_POSES_SCANNED = True

        layout = self.layout
        scene = context.scene

        if context.object is None or context.object.type != 'ARMATURE':
            return

        armature_object = context.object

        props = ["available_poses"]
        POSES_PROPERTIES.draw_properties(scene, layout, props)
        layout.operator('mpfb.load_pose')
        props = ["available_partials"]
        POSES_PROPERTIES.draw_properties(scene, layout, props)
        layout.operator('mpfb.load_partial')


ClassManager.add_class(MPFB_PT_ApplyPosePanel)
