"""Macro subpanel for modeling humans"""

import bpy, os, json
from bpy.props import FloatProperty
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb.entities.objectproperties import HumanObjectProperties

_LOG = LogService.get_logger("model.macrosubpanel")
_LOG.set_level(LogService.DEBUG)

_TARGETS_DIR = LocationService.get_mpfb_data("targets")
_LOG.debug("Target dir:", _TARGETS_DIR)

_INTERNAL_PREFIX = "mpfb_macropanel_"

_MACROTARGETS = {
        "Macrodetails": [
            "gender",
            "age",
            "muscle",
            "weight",
            "height",
            "proportions"
            ],
        "Breast shape": [
            "cupsize",
            "firmness"
            ],
        "Race": [
            "african",
            "asian",
            "caucasian"
            ]
    }

class MPFB_PT_Macro_Sub_Panel(bpy.types.Panel):
    """Human macro modeling panel."""

    bl_label = "phenotype"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "MPFB_PT_Model_Panel"
    bl_options = {'DEFAULT_CLOSED'}

    def _draw_category(self, scene, layout, category_name, targets, basemesh):
        box = layout.box()
        box.label(text=category_name)
        for target in targets:
            box.prop(scene, _INTERNAL_PREFIX + target)

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if not context.object:
            return

        if not ObjectService.object_is_basemesh(context.object):
            return

        basemesh = context.object

        for category_name in _MACROTARGETS.keys():
            targets = _MACROTARGETS[category_name]
            self._draw_category(scene, layout, category_name, targets, basemesh)

ClassManager.add_class(MPFB_PT_Macro_Sub_Panel)

_PROPS_DIR = os.path.join(LocationService.get_mpfb_root("entities"), "objectproperties", "humanproperties")

def _general_set_target_value(name, value):
    _LOG.trace("_general_set_target_value", (name, value))
    basemesh = bpy.context.object
    HumanObjectProperties.set_value(name, value, entity_reference=basemesh)
    TargetService.reapply_macro_details(basemesh)
    #===========================================================================
    # macro_info = TargetService.get_macro_info_dict_from_basemesh(basemesh)
    # _LOG.debug("macro_info", macro_info)
    # target_stack = TargetService.calculate_target_stack_from_macro_info_dict(macro_info)
    # _LOG.debug("target_stack", target_stack)
    #===========================================================================

def _general_get_target_value(name):
    basemesh = bpy.context.object
    value = HumanObjectProperties.get_value(name, entity_reference=basemesh)
    _LOG.trace("_general_get_target_value", (name, value))
    return value

for _main in _MACROTARGETS.keys():
    for _target in _MACROTARGETS[_main]:
        _getstr = "def _get_macro_target(self):\n"
        _getstr = _getstr + "    return _general_get_target_value(\"" + _target + "\")\n"
        exec(_getstr)

        _setstr = "def _set_macro_target(self, value):\n"
        _setstr = _setstr + "    _general_set_target_value(\"" + _target + "\", value)\n"
        exec(_setstr)

        _label = _target
        _description = _target
        _default = 0.5

        _propdef = os.path.join(_PROPS_DIR, _target + ".json")

        if os.path.exists(_propdef):
            with open(_propdef, "r") as json_file:
                _prop = json.load(json_file)
                _label = _prop["label"]
                _description = _prop["description"]
                _default = _prop["default"]

        prop = FloatProperty(name=_label, get=_get_macro_target, set=_set_macro_target, description=_description, max=1.0, min=0.0, default=_default)
        setattr(bpy.types.Scene, _INTERNAL_PREFIX + _target, prop)
