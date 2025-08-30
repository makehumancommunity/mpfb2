from ...services.logservice import LogService
from ...services.objectservice import ObjectService
from ...services.materialservice import MaterialService
from ...services.nodeservice import NodeService
from ...services.dynamicconfigset import DynamicConfigSet
from ...services.haireditorservices import HairEditorService

import bpy, os, re, json

_LOG = LogService.get_logger("ui.hairproperties")
#_LOG.set_level(LogService.DEBUG)

DYNAMIC_PREFIX="DHAI_"
DYNAMIC_PREFIX_FUR="DFAI_"

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

DYNAMIC_FUR_PROPS_DEFINITIONS = {
        "length": ("Set Hair Curve Profile", "Socket_1", (0.0, 20.0)),
        "density": ("Set Hair Curve Profile", "Socket_0", (0.0, 1.0)),
        "thickness": ("Set Hair Curve Profile", "Input_3", (0.0, 0.003)),
        "frizz": ("Frizz Hair Curves", "Input_3", (0.0,1.0)),
        "roll": ("Roll Hair Curves", "Input_10", (0.0,1.0)),
        "roll_radius": ("Roll Hair Curves", "Input_3", (0.001, 0.1)),
        "roll_length": ("Roll Hair Curves", "Input_2", (0.001, 0.1)),
        "clump": ("Clump Hair Curves", "Input_7", (0.0,1.0)),
        "clump_distance": ("Clump Hair Curves", "Input_9", (0.003, 0.05)),
        "clump_shape": ("Clump Hair Curves", "Input_6", (-1.0,1.0)),
        "clump_tip_spread": ("Clump Hair Curves", "Input_10", (0.0, 0.02)),
        "noise": ("Hair Curves Noise", "Input_3", (0.0, 1.0)),
        "noise_distance": ("Hair Curves Noise", "Input_14", (0.0, 0.1)),
        "noise_scale": ("Hair Curves Noise", "Input_11", (0.0, 20)),
        "noise_shape": ("Hair Curves Noise", "Input_2", (0.0, 1.0)),
        "curl": ("Curl Hair Curves", "Input_2", (0.0, 1.0)),
        "curl_guide_distance": ("Curl Hair Curves", "Input_4", (0.0, 0.1)),
        "curl_radius": ("Curl Hair Curves", "Input_7", (0.0, 0.1)),
        "curl_frequency": ("Curl Hair Curves", "Input_11", (0.0, 20.0)),
        "holes": ("Set Hair Curve Profile", "Socket_2", (0.0, 1.0)),
        "holes_scale": ("Set Hair Curve Profile", "Socket_3", (0.0, 200.0))
        }

DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS = {
        "color1": ("Color 1", (0.117, 0.093, 0.047, 1.0)),
        "color2": ("Color 2", (0.031, 0.016, 0.004, 1.0)),
        "color_noise_scale": ("Noise Scale", (0.0, 500.0)),
        "darken_root": ("Darken root", (0.0, 1.0)),
        "root_color_length": ("Root color length", (0.0, 1.0)),
        "use_texture": ("Use Texture Instead of Colors", False),
        "texture_path": ("Texture File Path", "")
        }

class HairGetterSetterFactory():

    def __init__(self, name, prefix=DYNAMIC_PREFIX, fur=False):
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
        self.is_material_property = False
        self.is_texture_property = False
        self.is_fur = fur

        self.base_prop_definitions = None
        self.base_prop_material_definition = None

        if fur:
            self.base_prop_definitions = DYNAMIC_FUR_PROPS_DEFINITIONS
            self.base_prop_material_definition = DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS
        else:
            self.base_prop_definitions = DYNAMIC_HAIR_PROPS_DEFINITIONS
            self.base_prop_material_definition = DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS

        self._attempt_deducing_from_hair()
        if not self.is_hair_property:
            self._attempt_deducing_from_material()

        if self.managed_to_deduce_property:
            self._interpolate_hair_object_name()

    def _attempt_deducing_from_hair(self):
        if "color" in self.full_property_name:
            # Break here to avoid clashing with properties from the other set
            return
        candidate = (None, None)
        for key in self.base_prop_definitions:
            if self.full_property_name.endswith(key):
                # Can't break here, since it will find "length" before "roll_length"
                candidate = (key, self.base_prop_definitions[key])
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

    def _attempt_deducing_from_material(self):
        candidate = (None, None)
        for key in self.base_prop_material_definition:
            if self.full_property_name.endswith(key):
                candidate = (key, self.base_prop_material_definition[key])
        if candidate[0] is None:
            return
        self.short_property_name = candidate[0]
        definition = candidate[1]

        self.modifier_name = definition[0]
        self.modifier_attribute = definition[1]
        if self.short_property_name in ["use_texture", "texture_path"]:
            self.is_texture_property = True
        else:
            self.is_material_property = True
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

    def _material_getter(self):
        _LOG.debug("Generating material getter for", self.full_property_name)
        def getter(source):
            # This is very chatty, using "trace" rather than "debug" for this method
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

            material = MaterialService.get_material(hair_obj)
            if material is None:
                _LOG.error("No material found for", hair_obj.name)
                return

            group_node = None
            for node in material.node_tree.nodes:
                if hasattr(node, "node_tree") and node.node_tree and str(node.node_tree.name).startswith("Hair shader EEVEE"):
                    group_node = node
                    break

            if group_node is None:
                _LOG.error("There is no group node in this material", (hair_obj.name, material, material.node_tree))
                return

            socket = NodeService.find_input_socket_by_identifier_or_name(
                group_node,
                socket_identifier=self.modifier_name,
                socket_name=self.modifier_name
                )
            if socket is None:
                _LOG.error("No such socket found in this group node", (hair_obj.name, self.modifier_name, group_node.inputs))
                return

            _LOG.debug("Returning socket default value", (socket, socket.default_value))
            return socket.default_value

        return getter

    def _material_setter(self):
        _LOG.debug("Generating material setter for", self.full_property_name)
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

            material = MaterialService.get_material(hair_obj)
            if material is None:
                _LOG.error("No material found for", hair_obj.name)
                return

            group_node = None
            for node in material.node_tree.nodes:
                if hasattr(node, "node_tree") and node.node_tree and str(node.node_tree.name).startswith("Hair shader EEVEE"):
                    group_node = node
                    break

            if group_node is None:
                _LOG.error("There is no group node in this material", (hair_obj.name, material, material.node_tree))
                return

            socket = NodeService.find_input_socket_by_identifier_or_name(
                group_node,
                socket_identifier=self.modifier_name,
                socket_name=self.modifier_name
                )
            if socket is None:
                _LOG.error("No such socket found in this group node", (hair_obj.name, self.modifier_name, group_node.inputs))
                return

            socket.default_value = value

        return setter

    def _texture_getter(self):
        _LOG.debug("Generating texture getter for", self.full_property_name)
        def getter(source):
            _LOG.debug("Invoking texture getter for", (
                source,
                self.full_property_name,
                self.short_property_name
            ))

            hair_obj = self._get_hair_object()
            if hair_obj is None:
                _LOG.error("No hair object found for", self.hair_object_name)
                return

            mat = MaterialService.get_material(hair_obj)
            if mat is None or not mat.use_nodes:
                _LOG.error("No usable material on", hair_obj.name)
                return

            # find material group node
            group_node = next(
                (n for n in mat.node_tree.nodes
                 if hasattr(n, "node_tree")
                 and n.node_tree
                 and n.node_tree.name.startswith("Hair shader EEVEE")),
                None
            )
            if group_node is None:
                _LOG.error("No hair shader group node in material", mat.name)
                return

            gtree = group_node.node_tree
            nodes = gtree.nodes
            links = gtree.links
            img_node = next((n for n in nodes if n.type == 'TEX_IMAGE'), None)

            # TEXTURE PATH PROPERTY: look for the image node inside the group
            if self.short_property_name == "texture_path":
                if img_node and img_node.image:
                    return bpy.path.abspath(img_node.image.filepath)
                return "Select texture path"

            # USE TEXTURE PROPERTY: simply read the group‐node input default
            else:
                if not img_node:
                    _LOG.debug("No image node found - texture is not used.")
                    return False

                # Check if image node is linked to any shader base color inputs
                shader_nodes = [
                    n for n in nodes
                    if n.bl_idname in ('ShaderNodeBsdfPrincipled', 'ShaderNodeBsdfHairPrincipled')
                ]

                for shader in shader_nodes:
                    inp = shader.inputs[0]  # 'Base Color'
                    for ln in inp.links:
                        if ln.from_node == img_node and ln.from_socket.name == "Color":
                            _LOG.debug("Texture node is actively linked.")
                            return True

                _LOG.debug("No texture link found.")
                return False
        return getter

    def _texture_setter(self):
        _LOG.debug("Generating texture setter for", self.full_property_name)
        def setter(source, value):
            _LOG.debug("Invoking texture setter for", (
                source,
                self.full_property_name,
                self.short_property_name
            ))

            hair_obj = self._get_hair_object()
            if hair_obj is None:
                _LOG.error("No hair object found for", self.hair_object_name)
                return

            mat = MaterialService.get_material(hair_obj)
            if mat is None or not mat.use_nodes:
                _LOG.error("No usable material on", hair_obj.name)
                return

            # find our group node (Despite its name, group node also supports cycles)
            group_node = next(
                (n for n in mat.node_tree.nodes
                 if hasattr(n, "node_tree")
                 and n.node_tree
                 and n.node_tree.name.startswith("Hair shader EEVEE")),
                None
            )
            if group_node is None:
                _LOG.error("No hair shader group node in material", mat.name)
                return

            # key for saving previous links from shader nodes
            storage_key = "_saved_base_color_links"

            # TEXTURE PATH: load the image and insert a new image texture node
            gtree = group_node.node_tree
            nodes = gtree.nodes
            links = gtree.links

            # find all principled/hair-principled shader nodes
            shader_nodes = [
                n for n in nodes if n.bl_idname in ('ShaderNodeBsdfPrincipled', 'ShaderNodeBsdfHairPrincipled')
            ]

            if self.short_property_name == "texture_path":
                # Store previous texture node to delete it later
                previous_tex_node = None
                for node in list(nodes):
                    if node.type == 'TEX_IMAGE':
                        previous_tex_node = node
                # Disconnect texture
                if previous_tex_node:
                    HairEditorService.restore_shader_links(previous_tex_node, shader_nodes, group_node, nodes, links, storage_key)

                # Remove texture
                if previous_tex_node:
                    nodes.remove(previous_tex_node)

                path = bpy.path.abspath(value)
                if not path or not os.path.isfile(path):
                    _LOG.info("Texture path invalid")
                    return
                try:
                    img = bpy.data.images.load(path, check_existing=True)
                except Exception as e:
                    _LOG.error("Cannot load image '%s': %s", path, e)
                    return

                tex_node = gtree.nodes.new('ShaderNodeTexImage')
                tex_node.image = img
                tex_node.label = os.path.basename(path)
                tex_node.location = (300, 200)

                # Join node to material
                store_links = storage_key not in group_node
                HairEditorService.join_texture_node_to_shader(tex_node, shader_nodes, group_node, links, storage_key, store_links)

                _LOG.debug("Added texture node %s", tex_node.name)
                return

            # USE TEXTURE: flip links on/off
            # find the texture IMG node
            img_node = next((n for n in nodes if (n.type == 'TEX_IMAGE')), None)

            if value:
                # return in case of no available texture, so it does not break the material
                if not img_node:
                    return
                # store and remove existing links
                store_links=True
                HairEditorService.join_texture_node_to_shader(img_node, shader_nodes, group_node, links, storage_key, store_links)

            else:
                # disconnect texture and restore links to color inputs
                HairEditorService.restore_shader_links(img_node, shader_nodes, group_node, nodes, links, storage_key)

        return setter

    def _hair_getter(self):
        _LOG.debug("Generating hair getter for", self.full_property_name)
        def getter(source):
            # This is very chatty, using "trace" rather than "debug" for this method
            _LOG.trace("Invoking getter for", (
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
            _LOG.trace("Modifier, value", (modifier, modifier[self.modifier_attribute]))
            return modifier[self.modifier_attribute]
        return getter

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
            _LOG.debug("Modifier, value before", (modifier, modifier[self.modifier_attribute]))
            modifier[self.modifier_attribute] = value
            _LOG.debug("Modifier, value mid", (modifier, modifier[self.modifier_attribute]))
            hair_obj.update_tag()
            bpy.context.view_layer.update()
            hair_obj.hide_viewport = True
            hair_obj.hide_viewport = False
            if hasattr(modifier, "node_group") and modifier.node_group:
                modifier.node_group.interface_update(bpy.context)
            _LOG.debug("Modifier, value after", (modifier, modifier[self.modifier_attribute]))
        return setter


    def generate_getter(self):
        if self.is_hair_property:
            return self._hair_getter()
        if self.is_material_property:
            return self._material_getter()
        if self.is_texture_property:
            return self._texture_getter()
        return None

    def generate_setter(self):
        if self.is_hair_property:
            return self._hair_setter()
        if self.is_material_property:
            return self._material_setter()
        if self.is_texture_property:
            return self._texture_setter()
        return None

def dynamic_setter_factory(configset, name):
    factory = HairGetterSetterFactory(name)
    return factory.generate_setter()

def dynamic_getter_factory(configset, name):
    factory = HairGetterSetterFactory(name)
    return factory.generate_getter()

def dynamic_setter_factory_fur(configset, name):
    factory = HairGetterSetterFactory(name, prefix=DYNAMIC_PREFIX_FUR, fur=True)
    return factory.generate_setter()

def dynamic_getter_factory_fur(configset, name):
    factory = HairGetterSetterFactory(name, prefix=DYNAMIC_PREFIX_FUR, fur=True)
    return factory.generate_getter()

_LOC = os.path.dirname(__file__)
HAIR_PROPERTIES_DIR = os.path.join(_LOC, "properties")
HAIR_PROPERTIES = DynamicConfigSet.from_definitions_in_json_directory(
    HAIR_PROPERTIES_DIR,
    prefix="HAI_",
    dynamic_prefix=DYNAMIC_PREFIX,
    setter_factory=dynamic_setter_factory,
    getter_factory=dynamic_getter_factory
    )

FUR_PROPERTIES = DynamicConfigSet(
    [],
    prefix="FAI_",
    dynamic_prefix=DYNAMIC_PREFIX_FUR,
    setter_factory=dynamic_setter_factory_fur,
    getter_factory=dynamic_getter_factory_fur
    )
