"""This service provides utility functions for working with shader nodes."""

import bpy
import bpy.types
from bpy.types import NodeSocketColor, ShaderNodeGroup, NodeGroupInput, NodeGroupOutput
import os

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("services.nodeservice")

_NODETYPETOCLASS = dict()
_NODETYPETOCLASS["BOOLEAN"] = "NodeSocketBool"
_NODETYPETOCLASS["COLLECTION"] = "NodeSocketCollection"
_NODETYPETOCLASS["CUSTOM"] = "NodeSocketFloat"
_NODETYPETOCLASS["GEOMETRY"] = "NodeSocketGeometry"
_NODETYPETOCLASS["IMAGE"] = "NodeSocketImage"
_NODETYPETOCLASS["INT"] = "NodeSocketInt"
_NODETYPETOCLASS["OBJECT"] = "NodeSocketObject"
_NODETYPETOCLASS["RGBA"] = "NodeSocketColor"
_NODETYPETOCLASS["SHADER"] = "NodeSocketShader"
_NODETYPETOCLASS["STRING"] = "NodeSocketString"
_NODETYPETOCLASS["VALUE"] = "NodeSocketFloat"
_NODETYPETOCLASS["VECTOR"] = "NodeSocketVector"


class NodeService:

    """Service with utility functions for working with shader nodes. It only has static methods, so you don't
    need to instance it."""

    def __init__(self):
        """Do not instance, there are only static methods in the class"""
        raise RuntimeError("You should not instance NodeService. Use its static methods instead.")

    @staticmethod
    def get_node_info(node):
        """Return a dict with information about a node, such as its input and output sockets,
        its class and its attributes."""

        _LOG.enter()
        _LOG.dump("node", node)
        node_info = dict()
        node_info["type"] = node.__class__.__name__
        node_info["name"] = node.name
        node_info["label"] = node.label
        node_info["location"] = list(node.location)
        node_info["create"] = True
        values = dict()
        if hasattr(node, "inputs"):
            for node_input in node.inputs:
                _LOG.dump("node_input", node_input)
                if node_input.__class__.__name__ in ["NodeSocketColor", "NodeSocketFloatFactor", "NodeSocketFloat"]:
                    if isinstance(node_input, NodeSocketColor):
                        values[node_input.name] = list(node_input.default_value)
                    else:
                        values[node_input.name] = node_input.default_value
        node_info["values"] = values
        if node_info["type"] == "ShaderNodeTexImage":
            NodeService._add_tex_image_info(node, node_info)
        if node_info["type"] == "ShaderNodeMath":
            node_info["operation"] = node.operation
            node_info["use_clamp"] = node.use_clamp
        if node_info["type"] == "ShaderNodeVectorMath":
            node_info["operation"] = node.operation
        if node_info["type"] == "ShaderNodeValue":
            node_info["value"] = node.outputs[0].default_value
        return node_info

    @staticmethod
    def get_socket_default_values(node):
        """Return a dict with the default values of all input sockets for a node."""
        _LOG.enter()
        values = dict()
        if hasattr(node, "inputs"):
            for node_input in node.inputs:
                _LOG.dump("node_input", node_input)
                if node_input.__class__.__name__ in ["NodeSocketColor", "NodeSocketFloatFactor", "NodeSocketFloat"]:
                    if isinstance(node_input, NodeSocketColor):
                        values[node_input.name] = list(node_input.default_value)
                    else:
                        values[node_input.name] = node_input.default_value
        else:
            _LOG.debug("Node did not have the inputs attribute")

        return values

    @staticmethod
    def set_socket_default_values(node, values):
        """Set the node's input socket default values to the values provided in the "values" dict."""
        _LOG.enter()
        if hasattr(node, "inputs"):
            for node_input in node.inputs:
                _LOG.dump("node_input", node_input)
                if node_input.__class__.__name__ in ["NodeSocketColor", "NodeSocketFloatFactor", "NodeSocketFloat"] and node_input.name in values:
                    node_input.default_value = values[node_input.name]
        else:
            _LOG.debug("Node did not have the inputs attribute")

    @staticmethod
    def _add_tex_image_info(node, node_info):
        node_info["colorspace"] = "sRGB"
        if node.image and node.image.colorspace_settings:
            node_info["colorspace"] = node.image.colorspace_settings.name
        node_info["filename"] = NodeService.get_image_file_path(node)

    @staticmethod
    def get_link_info(link):
        """Return a dict with information about a specific node link, ie a connection between one node's output
        socket and another node's input socket. The dict will contain info about both participating nodes and
        participating sockets."""

        _LOG.enter()

        link_info = dict()
        link_info["from_node"] = link.from_node.name
        link_info["to_node"] = link.to_node.name

        name_appears_multiple_times_in_from_node = False
        socket_output_number = 0
        current_output_number = 0
        for output in link.from_node.outputs:
            _LOG.dump("socket:", (output, link.from_socket, output == link.from_socket))
            if output == link.from_socket:
                socket_output_number = current_output_number
            if output != link.from_socket and output.name == link.from_socket.name:
                name_appears_multiple_times_in_from_node = True
            current_output_number = current_output_number + 1

        name_appears_multiple_times_in_to_node = False
        socket_input_number = 0
        current_input_number = 0
        for inp in link.to_node.inputs:
            if inp == link.to_socket:
                socket_input_number = current_input_number
            if inp != link.to_socket and inp.name == link.to_socket.name:
                name_appears_multiple_times_in_to_node = True
            current_input_number = current_input_number + 1

        if name_appears_multiple_times_in_from_node:
            _LOG.trace("Node with multiple output sockets of the same name", (link.from_node, link.from_socket.name))
            link_info["from_socket"] = socket_output_number
        else:
            link_info["from_socket"] = link.from_socket.name

        if name_appears_multiple_times_in_to_node:
            _LOG.trace("Node with multiple input sockets of the same name", (link.to_node, link.to_socket.name))
            link_info["to_socket"] = socket_input_number
        else:
            link_info["to_socket"] = link.to_socket.name

        if name_appears_multiple_times_in_from_node or name_appears_multiple_times_in_to_node:
            _LOG.dump("Multiple sockets of same name", (link.to_node, link.to_socket.name, link_info))

        return link_info

    @staticmethod
    def get_node_tree_as_dict(node_tree, recurse_groups=True, group_dict=None, recursion_level=0):
        """Return a dict describing an entire node tree, including node definitions, groups and links.
        Do not provide a value for recursion level manually, it is used when recursing into
        nested node groups."""

        _LOG.enter()
        _LOG.dump("node_tree", node_tree)

        for_output = dict()
        for_output["nodes"] = dict()
        for_output["links"] = []

        if recursion_level == 0:
            for_output["groups"] = dict()

        if group_dict is None:
            _LOG.debug("Group dict was not provided, at recursion level", recursion_level)
            group_dict = for_output["groups"]
        else:
            _LOG.debug("Provided group dict", group_dict.keys())

        nodes = node_tree.nodes

        if "groups" in for_output and recursion_level > 0:
            raise AttributeError('Found groups in deeper recursion level ' + str(recursion_level))

        if group_dict is None:
            raise AttributeError('group_dict is None')

        for node in nodes:
            node_info = NodeService.get_node_info(node)
            name = node_info["name"]
            for_output["nodes"][name] = node_info
            if isinstance(node, ShaderNodeGroup) and recurse_groups:
                group_name = node.node_tree.name
                for_output["nodes"][name]["group_name"] = group_name
                if not group_name in group_dict:
                    if not recurse_groups:
                        group_dict[group_name] = dict()
                    else:
                        group_dict[group_name] = NodeService.get_node_tree_as_dict(node.node_tree, recurse_groups=True, group_dict=group_dict, recursion_level=recursion_level + 1)
                group_dict[group_name]["inputs"] = {}
                group_dict[group_name]["outputs"] = {}
                for input_socket in node.node_tree.inputs:
                    group_dict[group_name]["inputs"][input_socket.name] = dict()
                    group_dict[group_name]["inputs"][input_socket.name]["type"] = _NODETYPETOCLASS[input_socket.type]
                    value = node.inputs.get(input_socket.name).default_value
                    if input_socket.type == "RGBA":
                        value = [value[0], value[1], value[2], value[3]]
                    if input_socket.type != "VECTOR":
                        group_dict[group_name]["inputs"][input_socket.name]["value"] = value
                for output_socket in node.node_tree.outputs:
                    group_dict[group_name]["outputs"][output_socket.name] = _NODETYPETOCLASS[output_socket.type]

        links = node_tree.links

        for link in links:
            for_output["links"].append(NodeService.get_link_info(link))

        _LOG.dump("nodes", for_output)
        return for_output

    @staticmethod
    def clear_node_tree(node_tree, also_destroy_groups=False):
        """Delete all nodes in a node tree. The tree instance as such will be preserved."""
        nodes = []
        for node in node_tree.nodes:
            _LOG.debug("Node", (node, isinstance(node, ShaderNodeGroup)))
            nodes.append(node)
            if also_destroy_groups and isinstance(node, ShaderNodeGroup):
                _LOG.debug("found group to destroy", (node, node.name, node.node_tree, node.node_tree.name))
                node.name = node.name + ".unused"
                node.node_tree.name = node.node_tree.name + ".unused"
        for node in nodes:
            node_tree.nodes.remove(node)

    @staticmethod
    def update_tex_image_with_settings_from_dict(node, node_info):
        """Set file name and colorspace information in an image texture node based on
        information in the provided dict. This will also load the file as an
        image object if this had not already been done."""

        file_name = os.path.basename(node_info["filename"])
        if not str(file_name).strip():
            _LOG.error("Trying to load image with null/empty filename")
            _LOG.error("node_info", node_info)
            return
        if file_name in bpy.data.images:
            _LOG.debug("image existed:", node_info["filename"])
            image = bpy.data.images[file_name]
        else:
            _LOG.debug("Will attempt to load file", node_info["filename"])
            if os.path.exists(node_info["filename"]):
                image = bpy.data.images.load(node_info["filename"])
            else:
                _LOG.error("File does not exist:", node_info["filename"])
                return
        if "colorspace" in node_info and node_info["colorspace"] != "Non-Color":
            image.colorspace_settings.name = node_info["colorspace"]
        else:
            image.colorspace_settings.name = "sRGB"
        node.image = image

    @staticmethod
    def update_node_with_settings_from_dict(node, node_info):
        """Set node attributes and input socket default values based on information
        in the provided dict."""

        if node_info["type"] == "ShaderNodeGroup":
            if "group_name" in node_info:
                group_name = node_info["group_name"]
            else:
                group_name = node_info["name"]
            if not group_name in bpy.data.node_groups:
                _LOG.error("Tried to assign a node tree which did not exist", node_info)
                raise ValueError("Tried to assign a node tree which did not exist")
            node.node_tree = bpy.data.node_groups.get(group_name)

        if "location" in node_info:
            node.location = node_info["location"]

        if node_info["type"] == "ShaderNodeTexImage":
            NodeService.update_tex_image_with_settings_from_dict(node, node_info)

        if node_info["type"] in ["ShaderNodeMath", "ShaderNodeVectorMath"]:
            if "operation" in node_info:
                node.operation = node_info["operation"]
            if "use_clamp" in node_info:
                node.use_clamp = node_info["use_clamp"]

        if node_info["type"] == "ShaderNodeValToRGB" and "stops" in node_info:
            elements = node.color_ramp.elements
            stops_in_node = len(elements)
            stops_in_info = len(node_info["stops"])
            while stops_in_node < stops_in_info:
                elements.new(1.0)
                stops_in_node = len(elements)
            i = 0
            for stop in elements:
                stop.position = node_info["stops"][i]
                i = i + 1

        if node_info["type"] == "ShaderNodeValue":
            node.outputs[0].default_value = node_info["value"]

        for value in node_info["values"]:
            if not value in node.inputs:
                _LOG.error("Found an input name which didn't exist as socket:", value)
            else:
                node.inputs[value].default_value = node_info["values"][value]

        node.name = node_info["name"]
        if "label" in node_info:
            node.label = node_info["label"]

    @staticmethod
    def _ensure_group_interfaces_exist(dict_with_node_tree, force_wipe_group_node_trees=False):
        _LOG.enter()
        if not "groups" in dict_with_node_tree or not dict_with_node_tree["groups"]:
            _LOG.debug("The node tree dict did not have a group definition hierarchy")
            return

        groups = dict_with_node_tree["groups"]
        for group_name in groups.keys():
            group = groups[group_name]
            group["pre_existing"] = False
            _LOG.debug("Starting to analyze group", group_name)
            if group_name in bpy.data.node_groups:
                node_tree = bpy.data.node_groups.get(group_name)
                if force_wipe_group_node_trees:
                    _LOG.warn("Wiping node tree", group_name)
                    NodeService.clear_node_tree(node_tree)
                else:
                    group["pre_existing"] = True
            else:
                node_tree = bpy.data.node_groups.new(group_name, type="ShaderNodeTree")

            input_node = None
            output_node = None

            for node in node_tree.nodes:
                if isinstance(node, NodeGroupInput):
                    input_node = node
                if isinstance(node, NodeGroupOutput):
                    output_node = node

            if input_node is None:
                input_node = node_tree.nodes.new("NodeGroupInput")
                input_node.name = "Group Input"

            if output_node is None:
                output_node = node_tree.nodes.new("NodeGroupOutput")
                output_node.name = "Group Output"

            if "inputs" in group:
                for input_name in group["inputs"].keys():
                    if not input_name in node_tree.inputs:
                        input_def = group["inputs"][input_name]
                        _LOG.debug("Missing input socket:", input_def)
                        create = True
                        if "create" in input_def:
                            create = input_def["create"]
                        if create:
                            input_socket = node_tree.inputs.new(input_def["type"], input_name)
                            if not "Vector" in input_def["type"]:
                                input_socket.default_value = input_def["value"]
                    else:
                        _LOG.debug("Input socket already existed:", input_name)

            if "outputs" in group:
                for output_name in group["outputs"].keys():
                    if not output_name in node_tree.outputs:
                        _LOG.debug("Missing output socket:", output_name)
                        node_tree.outputs.new(name=output_name, type=group["outputs"][output_name])
                    else:
                        _LOG.debug("Output socket already existed:", output_name)

    @staticmethod
    def apply_node_tree_from_dict(target_node_tree, dict_with_node_tree, wipe_node_tree=False):
        """Update an entire node tree based on information in the provided dict. The node tree
        must exist. This will also recursively update or create node groups if necessary."""

        _LOG.enter()

        if wipe_node_tree:
            NodeService.clear_node_tree(target_node_tree)

        NodeService._ensure_group_interfaces_exist(dict_with_node_tree)

        node_by_name = dict()

        if "groups" in dict_with_node_tree:
            groups = dict_with_node_tree["groups"]
            for group_name in groups.keys():
                group = groups[group_name]
                if not "pre_existing" in group or not group["pre_existing"]:
                    if group_name in bpy.data.node_groups:
                        node_tree = bpy.data.node_groups.get(group_name)
                        NodeService.apply_node_tree_from_dict(node_tree, group)
                    else:
                        raise ValueError('Found a group name that did not exist as a node tree. It should have been created ten lines above.')

        _LOG.dump("nodes", dict_with_node_tree["nodes"])

        for node_name in dict_with_node_tree["nodes"]:
            node_info = dict_with_node_tree["nodes"][node_name]
            if "create" not in node_info or node_info["create"]:
                _LOG.dump("Creating node", node_info)
                if node_info["type"] in ["NodeGroupInput", "NodeGroupOutput"]:
                    _LOG.trace("Found, as expeced, a", node_info["type"])
                    node_by_name[node_name] = target_node_tree.nodes.get(node_name)
                    if node_by_name[node_name] is None:
                        _LOG.error("Broken group I/O:", node_info)
                        raise ValueError('Could not find referenced group I/O')
                    else:
                        NodeService.update_node_with_settings_from_dict(node_by_name[node_name], node_info)
                else:
                    new_node = NodeService.create_node_from_dict(target_node_tree, node_info)
                    _LOG.dump("Created node", new_node)
                    node_by_name[node_name] = new_node
            else:
                _LOG.dump("Not creating node", node_info)

        links = target_node_tree.links

        for link in dict_with_node_tree["links"]:
            if link["from_node"] in node_by_name and link["to_node"] in node_by_name:
                from_node = node_by_name[link["from_node"]]
                to_node = node_by_name[link["to_node"]]
                if from_node is None:
                    _LOG.error("Broken link, from_node is None", link)
                    raise ValueError('Broken link: from_node is None')
                if to_node is None:
                    _LOG.error("Broken link, to_node is None", link)
                    raise ValueError('Broken link: to_node is None')

                from_socket_exists = False
                if isinstance(link["from_socket"], int):
                    from_socket_exists = True
                else:
                    from_socket_exists = link["from_socket"] in from_node.outputs

                to_socket_exists = False
                if isinstance(link["to_socket"], int):
                    to_socket_exists = True
                else:
                    to_socket_exists = link["to_socket"] in to_node.inputs

                if from_socket_exists and to_socket_exists:
                    from_socket = from_node.outputs[link["from_socket"]]
                    to_socket = to_node.inputs[link["to_socket"]]
                    if len(to_socket.links):
                        _LOG.warn("Socket already had a link:", link["to_socket"] + " " + link["to_node"])
                        raise ValueError('Broken link: socket already had a link')
                    links.new(from_socket, to_socket)
                else:
                    _LOG.warn("Broken link", link)
                    # raise ValueError('Broken link: socket on one side did not exist')
            else:
                _LOG.debug("At least one side of the link did not exist: " + link["from_node"] + " -> " + link["to_node"])

    @staticmethod
    def get_or_create_node_group(group_name):
        """Find a node tree with the given group name and return it. If it doesn't exist, then create it."""
        if group_name in bpy.data.node_groups:
            return bpy.data.node_groups.get(group_name)
        return bpy.data.node_groups.new(group_name, type="ShaderNodeTree")

    @staticmethod
    def find_node_by_name(node_tree, node_name):
        """Find a node with the given name in the node tree."""
        _LOG.enter()
        for node in node_tree.nodes:
            if node.name == node_name:
                return node
        return None

    @staticmethod
    def find_nodes_by_type_name(node_tree, type_name):
        """Return an array with all nodes of the given type in the node tree."""
        _LOG.enter()
        nodes = []
        for node in node_tree.nodes:
            _LOG.debug("node", node)
            _LOG.debug("node.type", node.type)
            _LOG.debug("node class", node.__class__.__name__)
            if type_name in [node.__class__.__name__, node.type]:
                nodes.append(node)
        return nodes

    @staticmethod
    def find_first_node_by_type_name(node_tree, type_name):
        """Find the first node with the given type in the node tree."""
        _LOG.enter()
        nodes = NodeService.find_nodes_by_type_name(node_tree, type_name)
        if nodes is None or len(nodes) < 1:
            _LOG.debug("Got an empty list of nodes for type", type_name)
            return None
        return nodes[0]

    @staticmethod
    def find_nodes_by_class(node_tree, type_class):
        """Return an array with all nodes of the given type class in the node tree."""
        _LOG.enter()
        nodes = []
        for node in node_tree.nodes:
            if isinstance(node, type_class):
                nodes.append(node)
        return nodes

    @staticmethod
    def find_first_node_by_class(node_tree, type_class):
        """Find the first node with the given type class in the node tree."""
        _LOG.enter()
        nodes = NodeService.find_nodes_by_class(node_tree, type_class)
        if nodes is None or len(nodes) < 1:
            return None
        return nodes[0]

    @staticmethod
    def find_socket_default_value(node, socket_name):
        """Return the default value of the node's input socket with the given name."""
        _LOG.enter()
        if not node:
            raise ValueError('Cannot find values on None node')
        if not node.inputs:
            _LOG.error("Node of type " + str(type(node)) + " didn't have any inputs!?")
            return None
        if not socket_name in node.inputs:
            _LOG.warn("Node of type " + str(type(node)) + " didn't have any input called ", socket_name)
            return None
        return node.inputs[socket_name].default_value

    @staticmethod
    def find_node_linked_to_socket(node_tree, node_which_is_linked_to, name_of_socket):
        """Return the node that links to an input socket in the given node."""
        _LOG.enter()
        if not node_which_is_linked_to or not name_of_socket:
            raise ValueError('Cannot find values on None node or socket')
        source_side_of_link = None
        for link in node_tree.links:
            if link.to_node == node_which_is_linked_to:
                if link.to_socket.name == name_of_socket:
                    source_side_of_link = link.from_node
        return source_side_of_link

    @staticmethod
    def get_image_file_path(image_texture_node):
        """Return the normalized file path of an image referred to by an image texture node."""
        _LOG.enter()
        if image_texture_node.image:
            if image_texture_node.image.filepath or image_texture_node.image.filepath_raw:
                if image_texture_node.image.filepath:
                    path = bpy.path.abspath(image_texture_node.image.filepath)
                    if os.path.isfile(path):
                        return path
                    _LOG.warn("Is not a file:", path)
                else:
                    return bpy.path.abspath(image_texture_node.image.filepath_raw)
            else:
                _LOG.warn("Found image texture with an image property, but the image had an empty file path.")
        else:
            _LOG.warn("Found an image texture, but its image property is empty.")
        return None

    @staticmethod
    def create_node(node_tree, type_name, name=None, label=None, xpos=0, ypos=0):
        """Create a new node with the given type."""
        _LOG.enter()
        new_node = node_tree.nodes.new(type_name)
        if not name is None:
            new_node.name = name
        if not label is None:
            new_node.label = label
        new_node.location = (xpos, ypos)
        return new_node

    @staticmethod
    def create_node_from_dict(node_tree, node_info):
        """Create a new node based on information in the provided dict."""
        new_node = node_tree.nodes.new(node_info["type"])
        NodeService.update_node_with_settings_from_dict(new_node, node_info)
        return new_node

    @staticmethod
    def create_principled_node(node_tree, name=None, label=None, xpos=0, ypos=0):
        """Create a new principled node."""
        _LOG.enter()
        return NodeService.create_node(node_tree, "ShaderNodeBsdfPrincipled", name=name, label=label, xpos=xpos, ypos=ypos)

    @staticmethod
    def create_bump_node(node_tree, name=None, label=None, xpos=0, ypos=0):
        """Create a new bump node."""
        _LOG.enter()
        return NodeService.create_node(node_tree, "ShaderNodeBump", name=name, label=label, xpos=xpos, ypos=ypos)

    @staticmethod
    def create_normal_map_node(node_tree, name=None, label=None, xpos=0, ypos=0):
        """Create a new normal map node."""
        _LOG.enter()
        return NodeService.create_node(node_tree, "ShaderNodeNormalMap", name=name, label=label, xpos=xpos, ypos=ypos)

    @staticmethod
    def create_displacement_node(node_tree, name=None, label=None, xpos=0, ypos=0):
        """Create a new displacement map node."""
        _LOG.enter()
        return NodeService.create_node(node_tree, "ShaderNodeDisplacement", name=name, label=label, xpos=xpos, ypos=ypos)

    @staticmethod
    def create_mix_rgb_node(node_tree, name=None, label=None, xpos=0, ypos=0):
        """Create a new mixrgb node."""
        _LOG.enter()
        return NodeService.create_node(node_tree, "ShaderNodeMixRGB", name=name, label=label, xpos=xpos, ypos=ypos)

    @staticmethod
    def create_value_node(node_tree, name=None, label=None, xpos=0, ypos=0, default_value=0.0):
        """Create a new value node."""
        _LOG.enter()
        return NodeService.create_node(node_tree, "ShaderNodeValue", name=name, label=label, xpos=xpos, ypos=ypos)

    @staticmethod
    def create_attibute_node(node_tree, name=None, label=None, xpos=0, ypos=0, default_value=""):
        """Create a new attribute node."""
        _LOG.enter()
        return NodeService.create_node(node_tree, "ShaderNodeAttribute", name=name, label=label, xpos=xpos, ypos=ypos)

    @staticmethod
    def create_image_texture_node(node_tree, name=None, label=None, xpos=0, ypos=0, image_path_absolute=None, colorspace="sRGB"):
        """Create a new image texture node."""
        _LOG.enter()
        new_texture_node = NodeService.create_node(node_tree, "ShaderNodeTexImage", name=name, label=label, xpos=xpos, ypos=ypos)
        if image_path_absolute:
            image_file_name = os.path.basename(image_path_absolute)
            if image_file_name in bpy.data.images:
                _LOG.debug("image was previously loaded", image_path_absolute)
                image = bpy.data.images[image_file_name]
            else:
                image = bpy.data.images.load(image_path_absolute)
            image.colorspace_settings.name = colorspace
            new_texture_node.image = image
        return new_texture_node
