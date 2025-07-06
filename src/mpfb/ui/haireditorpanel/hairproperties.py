from ...services.logservice import LogService
from ...services.objectservice import ObjectService
from ...services.dynamicconfigset import DynamicConfigSet
from ...services.haireditorservices import HairEditorService
import bpy, os, re

_LOG = LogService.get_logger("ui.hairproperties")
_LOG.set_level(LogService.DEBUG)

DYNAMIC_HAIR_PROPS_DEFINITIONS = {
        "length": ("Set Hair Curve Profile", "Socket_1", (0.0, 10.0)),
        "density": ("Set Hair Curve Profile", "Socket_0", (0.0, 1.0)),
        "thickness": ("Set Hair Curve Profile", "Input_3", (0.0, 0.003)),
        "frizz": ("Frizz Hair Curves", "Input_3", (0.0,1.0)),
        "roll": ("Roll Hair Curves", "Input_10", (0.0,1.0)),
        "roll_radius": ("Roll Hair Curves", "Input_3", (0.001, 0.005)),
        "roll_length": ("Roll Hair Curves", "Input_2", (0.001, 0.1)),
        "clump": ("Clump Hair Curves", "Input_7", (0.0,1.0)),
        "clump_distance": ("Clump Hair Curves", "Input_9", (0.003, 0.05)),
        "clump_shape": ("Clump Hair Curves", "Input_6", (-1.0,1.0)),
        "clump_tip_spread": ("Clump Hair Curves", "Input_10", (0.0, 0.02)),
        "noise": ("Hair Curves Noise", "Input_3", (0.0, 1.0)),
        "noise_distance": ("Hair Curves Noise", "Input_14", (0.0, 0.01)),
        "noise_scale": ("Hair Curves Noise", "Input_11", (0.0, 20)),
        "noise_shape": ("Hair Curves Noise", "Input_2", (0.0, 1.0)),
        "curl": ("Curl Hair Curves", "Input_2", (0.0, 1.0)),
        "curl_guide_distance": ("Curl Hair Curves", "Input_4", (0.0, 0.1)),
        "curl_radius": ("Curl Hair Curves", "Input_7", (0.0, 0.1)),
        "curl_frequency": ("Curl Hair Curves", "Input_11", (0.0, 20.0))
        }

def _get_propdef(name):
    candidate = (None, None)
    for key in DYNAMIC_HAIR_PROPS_DEFINITIONS:
        if name.endswith(key):
            # Can't break here, since it will find "length" before "roll_length"
            candidate = (key, DYNAMIC_HAIR_PROPS_DEFINITIONS[key])
    return candidate

def _get_basemesh():
    if bpy.context and hasattr(bpy.context, "object"):
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.object)
        return basemesh
    return None

def _get_hair_object(name):
    if not name:
        return None
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    return None

def dynamic_setter_factory(configset, name):
    (propname, definition) = _get_propdef(name)

    if propname is None:
        _LOG.error("No definition found for", name)
        return None

    hair_name = re.sub("^DHAI_", "", name)
    hair_name = re.sub("_" + propname + "$", "", hair_name)

    _LOG.debug("Creating dynamic getter for", (name, propname, hair_name))

    def setter(self, value):
        basemesh = _get_basemesh()
        modifier_name = definition[0]
        modifier_attr = definition[1]
        _LOG.debug("Invoking setter for", (name, basemesh, modifier_name, modifier_attr))
        if basemesh is None:
            _LOG.error("No active basemesh found when trying to execute getter", name)
            return
        hair_obj = _get_hair_object(hair_name) # Should probably look for a relative of basemesh here
        if hair_obj is None:
            _LOG.error("No hair object found for", hair_name)
            return
        mod = hair_obj.modifiers[modifier_name]
        mod[modifier_attr] = value
        hair_obj.update_tag()
        bpy.context.view_layer.update()
        hair_obj.hide_viewport = True
        hair_obj.hide_viewport = False
        if hasattr(mod, "node_group") and mod.node_group:
            mod.node_group.interface_update(bpy.context)

    return setter

def dynamic_getter_factory(configset, name):
    (propname, definition) = _get_propdef(name)

    if propname is None:
        _LOG.error("No definition found for", name)
        return None

    hair_name = re.sub("^DHAI_", "", name)
    hair_name = re.sub("_" + propname + "$", "", hair_name)

    _LOG.debug("Creating dynamic getter for", (name, propname, hair_name))

    def getter(self):
        basemesh = _get_basemesh()
        modifier_name = definition[0]
        modifier_attr = definition[1]
        _LOG.trace("Invoking getter for", (name, basemesh, modifier_name, modifier_attr))
        if basemesh is None:
            _LOG.error("No active basemesh found when trying to execute getter", name)
            return
        hair_obj = _get_hair_object(hair_name) # Should probably look for a relative of basemesh here
        if hair_obj is None:
            _LOG.error("No hair object found for", hair_name)
            return
        return hair_obj.modifiers[modifier_name][modifier_attr]

    return getter

_LOC = os.path.dirname(__file__)
HAIR_PROPERTIES_DIR = os.path.join(_LOC, "properties")
HAIR_PROPERTIES = DynamicConfigSet.from_definitions_in_json_directory(
    HAIR_PROPERTIES_DIR,
    prefix="HAI_",
    dynamic_prefix="DHAI_",
    setter_factory=dynamic_setter_factory,
    getter_factory=dynamic_getter_factory
    )


