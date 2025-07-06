from ...services.logservice import LogService
from ...services.objectservice import ObjectService
from ...services.dynamicconfigset import DynamicConfigSet
from ...services.haireditorservices import HairEditorService
import bpy, os, re

_LOG = LogService.get_logger("ui.hairproperties")
_LOG.set_level(LogService.DEBUG)

DYNAMIC_PREFIX="DHAI_"

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

DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS = {
        "color1": ("Color 1", (0.117, 0.093, 0.047, 1.0)),
        "color2": ("Color 2", (0.031, 0.016, 0.004, 1.0)),
        "color_noise_scale": ("Noise Scale", (0.0, 500.0)),
        "darken_root": ("Darken root", (0.0, 1.0)),
        "root_color_length": ("Root color length", (0.0, 1.0))
        }

class HairGetterSetterFactory():

    def __init__(self, name, prefix=DYNAMIC_PREFIX):
        self.prefix = prefix
        self.full_property_name = name
        self.short_property_name = None
        self.property_metadata = None
        self.hair_object_name = None
        self.managed_to_deduce_property = False
        self.modifier_name = None
        self.modifier_attribute = None
        self.max = 0.0
        self.min = 0.0
        self.default_value = None
        self.is_hair_property = False

        self._attempt_deducing_from_hair()

        if self.managed_to_deduce_property:
            self._interpolate_hair_object_name()

    def _attempt_deducing_from_hair(self):
        candidate = (None, None)
        for key in DYNAMIC_HAIR_PROPS_DEFINITIONS:
            if self.full_property_name.endswith(key):
                # Can't break here, since it will find "length" before "roll_length"
                candidate = (key, DYNAMIC_HAIR_PROPS_DEFINITIONS[key])
        if candidate[0] is None:
            return
        self.short_property_name = candidate[0]
        definition = candidate[1]

        self.modifier_name = definition[0]
        self.modifier_attribute = definition[1]
        self.min = definition[2][0]
        self.max = definition[2][1]
        self.is_hair_property = True
        self.managed_to_deduce_property = True

    def _interpolate_hair_object_name(self):
        hair_name = re.sub("^" + self.prefix, "", self.full_property_name)
        hair_name = re.sub("_" + self.short_property_name + "$", "", hair_name)
        self.hair_object_name = hair_name

    def _get_hair_object(self):
        if not self.hair_object_name:
            return None
        if self.hair_object_name in bpy.data.objects:
            return bpy.data.objects[self.hair_object_name]
        return None

    def _get_basemesh(self):
        if bpy.context and hasattr(bpy.context, "object"):
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.object)
            return basemesh
        return None

    def _hair_getter(self):
        _LOG.debug("Generating hair getter for", self.full_property_name)
        def getter(source):
            _LOG.debug("Invoking getter for", (
                source,
                self.full_property_name,
                self.short_property_name,
                self.modifier_name,
                self.modifier_attribute
                ))
            hair_obj = self._get_hair_object()
            if hair_obj is None:
                _LOG.error("No hair object found for", self.hair_object_name)
                return
            modifier = hair_obj.modifiers[self.modifier_name]
            return modifier[self.modifier_attribute]
        return None

    def _hair_setter(self):
        _LOG.debug("Generating hair setter for", self.full_property_name)
        def setter(source, value):
            _LOG.debug("Invoking setter for", (
                source,
                self.full_property_name,
                self.short_property_name,
                self.modifier_name,
                self.modifier_attribute,
                value
                ))
            hair_obj = self._get_hair_object()
            if hair_obj is None:
                _LOG.error("No hair object found for", self.hair_object_name)
                return
            modifier = hair_obj.modifiers[self.modifier_name]
            modifier[self.modifier_attribute] = value
        return setter

    def generate_getter(self):
        if self.is_hair_property:
            return self._hair_getter()
        return None

    def generate_setter(self):
        if self.is_hair_property:
            return self._hair_setter()
        return None

def dynamic_setter_factory(configset, name):
    factory = HairGetterSetterFactory(name)
    return factory.generate_setter()
#===============================================================================
# The following works, but makes the creation of the setter extremely slow
# When commented out, the hair object no longer gets updated when changing properties
#
#         hair_obj.update_tag()
#         bpy.context.view_layer.update()
#         hair_obj.hide_viewport = True
#         hair_obj.hide_viewport = False
#         if hasattr(mod, "node_group") and mod.node_group:
#             mod.node_group.interface_update(bpy.context)
#===============================================================================

def dynamic_getter_factory(configset, name):
    factory = HairGetterSetterFactory(name)
    return factory.generate_getter()

_LOC = os.path.dirname(__file__)
HAIR_PROPERTIES_DIR = os.path.join(_LOC, "properties")
HAIR_PROPERTIES = DynamicConfigSet.from_definitions_in_json_directory(
    HAIR_PROPERTIES_DIR,
    prefix="HAI_",
    dynamic_prefix="DHAI_",
    setter_factory=dynamic_setter_factory,
    getter_factory=dynamic_getter_factory
    )


