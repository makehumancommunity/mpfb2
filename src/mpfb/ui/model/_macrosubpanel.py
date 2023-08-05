"""Macro subpanel for modeling humans"""

import bpy, os, json
from bpy.props import FloatProperty
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService
from mpfb.services.uiservice import UiService
from mpfb.entities.objectproperties import HumanObjectProperties

_LOG = LogService.get_logger("model.macrosubpanel")

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
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def _draw_category(self, scene, layout, category_name, targets, basemesh):
        box = layout.box()
        box.label(text=category_name)

        from mpfb.ui.model.modelpanel import MODEL_PROPERTIES
        filter = MODEL_PROPERTIES.get_value("filter", entity_reference=bpy.context.scene)

        for target in targets:
            if not str(filter) or str(filter).lower() in str(target).lower():
                box.prop(scene, _INTERNAL_PREFIX + target)
            else:
                print("Not matching " + str(filter).lower() + " -> " + str(target).lower())

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")
        if not basemesh:
            return

        for category_name in _MACROTARGETS.keys():
            targets = _MACROTARGETS[category_name]
            self._draw_category(scene, layout, category_name, targets, basemesh)

ClassManager.add_class(MPFB_PT_Macro_Sub_Panel)

_PROPS_DIR = os.path.join(LocationService.get_mpfb_root("entities"), "objectproperties", "humanproperties")

def _general_set_target_value(name, value):
    _LOG.trace("_general_set_target_value", (name, value))
    basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")
    HumanObjectProperties.set_value(name, value, entity_reference=basemesh)
    from mpfb.ui.model.modelpanel import MODEL_PROPERTIES
    prune = MODEL_PROPERTIES.get_value("prune", entity_reference=bpy.context.scene)
    ObjectService.activate_blender_object(basemesh)
    TargetService.reapply_macro_details(basemesh, remove_zero_weight_targets=prune)
    if MODEL_PROPERTIES.get_value("refit", entity_reference=bpy.context.scene):
        HumanService.refit(basemesh)

def _general_get_target_value(name):
    basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")
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
