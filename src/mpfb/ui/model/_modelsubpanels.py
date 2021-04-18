"""Target subpanels for modeling humans"""

import bpy, os
from operator import itemgetter
from bpy.props import BoolProperty
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = LogService.get_logger("model.modelsubpanel")

_TARGETS_DIR = LocationService.get_mpfb_data("targets")
_TARGETS_CATEGORIES = []

_LOG.debug(_TARGETS_DIR)

for name in os.listdir(_TARGETS_DIR):
    _LOG.debug(name)
    if os.path.isdir(os.path.join(_TARGETS_DIR, name)) and not name in [".", "macrodetails"]:
        _TARGETS_CATEGORIES.append(name)

_TARGETS_CATEGORIES.sort()

class _Abstract_Model_Panel(bpy.types.Panel):
    """Human modeling panel."""

    bl_label = "SHOULD BE OVERRIDDEN"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "MPFB_PT_Model_Panel"
    bl_options = {'DEFAULT_CLOSED'}
    target_dir = "-"
    target_list = []
    category_names = []
    categories = dict()

    def _target_filename_to_category(self, target):
        name = str(target).replace(".target.gz", "")

        category_suffix = ""

        if name.endswith("-decr") or name.endswith("-incr"):
            category_suffix = "-decr-incr"

        if name.endswith("-in") or name.endswith("-out"):
            category_suffix = "-in-out"

        if name.endswith("-down") or name.endswith("-up"):
            category_suffix = "-down-up"

        for strip in ["-decr", "-incr", "-down", "-up", "-in", "-out"]:
            name = name.replace(strip, "")

        if str(name).startswith("r-"):
            name = name[2:]

        if str(name).startswith("l-"):
            name = name[2:]

        return name + category_suffix

    def _target_filename_to_label(self, target):
        label = str(target).replace(".target.gz", "")
        label = label.replace("-decr", " increase")
        label = label.replace("-incr", " decrease")
        label = label.replace("-down", " down")
        label = label.replace("-up", " up")
        label = label.replace("-in", " in")
        label = label.replace("-out", " out")
        label = label.replace("-", " ")
        label = label.replace(".", " ")

        if str(target).startswith("r-"):
            label = label[2:] + " (right)"

        if str(target).startswith("l-"):
            label = label[2:] + " (left)"

        return label

    def _rebuild_target_list(self):
        self.target_list = []
        self.categories = dict()
        self.category_names = []
        targets = []
        for name in os.listdir(self.target_dir):
            if not (str(name).startswith("female-") and self.bl_label == "breast"):
                targets.append(name)
        targets.sort()

        _LOG.dump("Target files", targets)

        for target in targets:
            category = self._target_filename_to_category(target)
            if not category in self.category_names:
                self.category_names.append(category)
            target_hash = {
                "name": str(target).replace(".target.gz", ""),
                "label": self._target_filename_to_label(target),
                "target": target,
                "category": category
                }
            self.target_list.append(target_hash)
            if not category in self.categories:
                self.categories[category] = []
            self.categories[category].append(target_hash)

        #self.target_list.sort(key=itemgetter('label'))
        self.category_names.sort()

        _LOG.dump("Target list", self.target_list)
        _LOG.dump("Category names", self.category_names)

    def _draw_targets(self, scene, layout):
        for category_name in self.category_names:
            box = layout.box()
            box.label(text=category_name)
            for targdef in self.categories[category_name]:
                _LOG.dump("targdef", targdef)
                op = box.operator('mpfb.add_target', text=targdef["label"])
                op.target_file = targdef["target"]
                op.target_name = targdef["name"]
                op.target_dir = self.target_dir

    def draw(self, context):
        _LOG.enter()
        if not self.target_list or len(self.target_list) < 1:
            self._rebuild_target_list()
        layout = self.layout
        scene = context.scene
        _LOG.dump("target_dir", self.target_dir)
        self._draw_targets(scene, layout)

for name in _TARGETS_CATEGORIES:
    sub_panel = type("MPFB_PT_Model_Sub_Panel_" + name, (_Abstract_Model_Panel, ), {
        "bl_label": name,
        "target_dir": os.path.join(_TARGETS_DIR, name)
        })
    ClassManager.add_class(sub_panel)
