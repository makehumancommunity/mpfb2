"""Measure subpanel for modeling humans"""

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

_LOG = LogService.get_logger("model.measuresubpanel")
_LOG.set_level(LogService.TRACE) # Remove this line when code is stable.

_INTERNAL_PREFIX = "mpfb_measurepanel_"

_MEASURETARGETS = {
    "arms": [
        "lowerarm-length",
        "upperarm-circ",
        "upperarm-length"
        ],
    "hands": [
        "wrist-circ",
        ],
    "legs": [
        "calf-circ",
        "knee-circ",
        "lowerleg-height",
        "thigh-circ",
        "upperleg-height"
        ],
    "feet": [
        "ankle-circ",
        ],
    "neck": [
        "circ",
        "height"
        ],
    "torso": [
        "bust-circ",
        "frontchest-dist",
        "hips-circ",
        "napetowaist-dist",
        "shoulder-dist",
        "underbust-circ",
        "waist-circ",
        "waisttohip-dist"
        ]
    }

class MPFB_PT_Measure_Sub_Panel(bpy.types.Panel):
    """Panel with measure model sliders"""

    bl_label = "measure"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "MPFB_PT_Model_Panel"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def _draw_category(self, scene, layout, category_name, targets, basemesh):
        box = layout.box()
        box.label(text=category_name)

        for target in targets:
            target_name_base = "measure-" + target
            box.prop(scene, _INTERNAL_PREFIX + target_name_base)

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")
        if not basemesh:
            return

        for category_name in _MEASURETARGETS.keys():
            targets = _MEASURETARGETS[category_name]
            self._draw_category(scene, layout, category_name, targets, basemesh)

ClassManager.add_class(MPFB_PT_Measure_Sub_Panel)

def _general_set_target_value(name, value):
    _LOG.trace("_general_set_target_value", (name, value))
    basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")
    from mpfb.ui.model.modelpanel import MODEL_PROPERTIES
    ObjectService.activate_blender_object(basemesh)

    # Core logic for converting is in TargetService.py
    TargetService.set_measure_target_value(basemesh, name, value)

    if MODEL_PROPERTIES.get_value("refit", entity_reference=bpy.context.scene):
        HumanService.refit(basemesh)

def _general_get_target_value(name):
    _LOG.trace("_general_get_target_value", name)
    basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")

    # Core logic for converting is in TargetService.py
    value = TargetService.get_measure_target_value(basemesh, name)

    return value

for _main in _MEASURETARGETS.keys():
    for _target in _MEASURETARGETS[_main]:

        _target_name_base = "measure-" + _target # + incr/decr

        _getstr = "def _get_measure_target(self):\n"
        _getstr = _getstr + "    return _general_get_target_value(\"" + _target_name_base + "\")\n"
        exec(_getstr)

        _setstr = "def _set_measure_target(self, value):\n"
        _setstr = _setstr + "    _general_set_target_value(\"" + _target_name_base + "\", value)\n"
        exec(_setstr)

        _label = _target
        _description = _target_name_base
        _default = 0.0

        # Something will have to be done about the max/min values of the following line. These would need to be real-world values somehow.
        prop = FloatProperty(name=_label, get=_get_measure_target, set=_set_measure_target, description=_description, max=1.0, min=-1.0, default=_default)
        setattr(bpy.types.Scene, _INTERNAL_PREFIX + _target_name_base, prop)
