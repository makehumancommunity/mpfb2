"""Macro subpanel for modeling humans"""

import bpy, os, json
from bpy.props import FloatProperty
from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import ObjectService
from ...services import HumanService
from ...services import TargetService
from ...services import UiService
from ...entities.objectproperties import HumanObjectProperties

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

        from ..model.modelpanel import MODEL_PROPERTIES
        filter = MODEL_PROPERTIES.get_value("filter", entity_reference=bpy.context.scene)

        for target in targets:
            if not str(filter) or str(filter).lower() in str(target).lower():
                box.prop(scene, _INTERNAL_PREFIX + target)

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

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")
        if basemesh is None:
            return False
        return TargetService.has_any_shapekey(basemesh)


ClassManager.add_class(MPFB_PT_Macro_Sub_Panel)

_PROPS_DIR = os.path.join(LocationService.get_mpfb_root("entities"), "objectproperties", "humanproperties")

# The following code is here for dynamically creating macro target properties. The general theory is that we
# iterate through the macro targets and create a FloatProperty instance for each one. This property gets
# dynamically created getter and setter methods, which calls the _general_get_target_value and _general_set_target_value
# methods for the respective target.

def _general_set_target_value(name, value):
    _LOG.trace("_general_set_target_value", (name, value))
    basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")

    HumanObjectProperties.set_value(name, value, entity_reference=basemesh)
    from ..model.modelpanel import MODEL_PROPERTIES
    prune = MODEL_PROPERTIES.get_value("prune", entity_reference=bpy.context.scene)
    ObjectService.activate_blender_object(basemesh)
    TargetService.reapply_macro_details(basemesh, remove_zero_weight_targets=prune)

    # If 'refit' is enabled, perform a refit operation on the basemesh
    if MODEL_PROPERTIES.get_value("refit", entity_reference=bpy.context.scene):
        HumanService.refit(basemesh)

def _general_get_target_value(name):
    basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")
    value = HumanObjectProperties.get_value(name, entity_reference=basemesh)
    _LOG.trace("_general_get_target_value", (name, value))
    return value

def _macro_getter_factory(target):
    """Create a getter function for the given target."""
    def _get_macro_target(self):
        return _general_get_target_value(target)
    return _get_macro_target

def _macro_setter_factory(target):
    """Create a setter function for the given target"""
    def _set_macro_target(self, value):
        return _general_set_target_value(target, value)
    return _set_macro_target

# Iterate through all macro targets defined in _MACROTARGETS
for _main in _MACROTARGETS.keys():
    for _target in _MACROTARGETS[_main]:
        # Create getter and setter functions for this specific target
        _get_macro_target = _macro_getter_factory(_target)
        _set_macro_target = _macro_setter_factory(_target)

        # Set default values for the property
        _label = _target
        _description = _target
        _default = 0.5

        # Construct the path to the JSON property definition file
        _propdef = os.path.join(_PROPS_DIR, _target + ".json")

        # If a JSON definition file exists, load and use its values
        if os.path.exists(_propdef):
            with open(_propdef, "r") as json_file:
                _prop = json.load(json_file)
                _label = _prop["label"]
                _description = _prop["description"]
                _default = _prop["default"]

        # Create a FloatProperty for the target
        prop = FloatProperty(name=_label, get=_get_macro_target, set=_set_macro_target, description=_description, max=1.0, min=0.0, default=_default)

        # Add the property to the Scene class with a prefix
        setattr(bpy.types.Scene, _INTERNAL_PREFIX + _target, prop)
