"""This service provides utility functions for working with shader nodes."""

import bpy
import bpy.types
from bpy.types import NodeSocketColor, ShaderNodeGroup, NodeGroupInput, NodeGroupOutput
import os
import typing
from typing import Any

from ..types import NodeInfo, NodeTreeDict, SocketValues
from .logservice import LogService
from .nodetreeservice import NodeTreeService, SocketInOut

_LOG = LogService.get_logger("services.nodeservice")

# On socket default values: bpy.types.NodeSocket does not declare default_value. It is declared on
# each concrete socket subclass instead, which is what this module's own hasattr() guards
# acknowledge. Where the subclass is known -- a NodeSocketColor behind an isinstance test, say --
# the read casts to it. Where it is not, because the method handles every socket type one node
# carries, the cast is to Any: the value is a float for one socket and a four element colour for
# the next, so naming a single subclass would be a guess rather than a narrowing.

NodeInfoV2 = dict[str, Any]
"""The version 2 description of a single node, as ``get_v2_node_info()`` writes it.

``class`` holds the node's class name. ``inputs`` and ``outputs`` map a prefixed socket name --
``"Input_Socket_" + name`` and ``"Output_Socket_" + name`` -- to a dict carrying that socket's
``name``, ``identifier``, ``class``, ``value_type`` and ``default_value``, plus ``min_value`` and
``max_value`` for a float socket on a group node. ``attributes`` maps each of the node's own RNA
property names to a dict carrying its ``name``, ``class`` and ``value``.

Where the version 1 ``NodeInfo`` is a recipe for recreating a node, this is a description of one,
and it is what the developer operators write the generated node wrappers under
``entities/nodemodel`` from. It is declared here rather than in ``src/mpfb/types.py`` because
nothing in scope reads one: this service is the only producer and the only consumers are three
operators in the UI layer.

An alias rather than a ``TypedDict`` for the same reason as ``NodeInfo``: ``min_value`` and
``max_value`` appear only for some sockets, and the attribute values are whatever RNA holds."""

LinkInfo = dict[str, str | int]
"""One link in a node tree: which nodes it joins and at which sockets.

``from_node`` and ``to_node`` are node names. ``from_socket`` and ``to_socket`` are socket names,
except where the node carries more than one socket of that name, in which case the index of the
socket is written instead -- which is why the value type is a union and not just ``str``.
``apply_node_tree_from_dict()`` tells the two apart with ``isinstance(..., int)``.

Local rather than shared because a ``LinkInfo`` only ever travels inside a ``NodeTreeDict``: this
service is the only module in scope which reads one by itself."""

_NODETYPETOCLASS: dict[str, str] = dict()
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

_INTERNAL_NODE_CLASS_ATTRIBUTES: list[str] = [
    '__doc__',
    '__module__',
    '__slots__',
    'bl_description',
    'bl_height_default',
    'bl_height_max',
    'bl_height_min',
    'bl_icon',
    'bl_idname',
    'bl_label',
    'bl_rna',
    'bl_static_type',
    'bl_width_default',
    'bl_width_max',
    'bl_width_min'
    ]

_BLACKLISTED_NODE_CLASS_ATTRIBUTES: list[str] = [
    'dimensions',
    'draw_buttons',
    'draw_buttons_ext',
    'hide',
    'input_template',
    'inputs',
    'interface',
    'internal_links',
    'is_registered_node_type',
    'label',
    'mute',
    'name',
    'node_tree',
    'output_template',
    'outputs',
    'parent',
    'poll',
    'poll_instance',
    'rna_type',
    'select',
    'show_options',
    'show_preview',
    'show_texture',
    'socket_value_update',
    'type',
    'update',
    'width_hidden'
    ]

_BLACKLISTED_ATTRIBUTE_TYPES: list[str] = [
    'bpy_func',
    'ColorMapping',
    'ColorRamp',
    'CurveMapping',
    'TexMapping',
    'ImageUser'
    ]

_KNOWN_SHADER_NODE_CLASSES: list[type[bpy.types.ShaderNode]] = []

for subc in dir(bpy.types):
    try:
        obj = getattr(bpy.types, subc)
        if hasattr(obj, "__bases__") and bpy.types.ShaderNode in obj.__bases__:
            _KNOWN_SHADER_NODE_CLASSES.append(obj)
    except Exception as e:
        _LOG.error("An unexpected error occurred while listing shader classes", (subc, e))


class NodeService:

    """The NodeService class provides a collection of static methods for managing and manipulating node trees and nodes within
    Blender's shader node system. It includes functionalities for:

    - Creating and destroying nodes and node trees
    - Retrieving information about nodes and sockets
    - Managing node groups
    - Creating, finding and setting the value for sockets
    - Finding and linking nodes within a node tree

    In summary, the NodeService class is designed to facilitate the manipulation and querying of Blender's node-based shader
    system programmatically."""

    def __init__(self) -> None:
        """Do not instance, there are only static methods in the class"""
        raise RuntimeError("You should not instance NodeService. Use its static methods instead.")

    @staticmethod
    def create_node_tree(node_tree_name: str, inputs: list[Any] | None = None, outputs: list[Any] | None = None) -> bpy.types.ShaderNodeTree:
        """
        Create a new shader node tree with the given name.

        Parameters:
        - node_tree_name: The name of the new node tree.
        - inputs: Optional list of input sockets to add to the node tree.
        - outputs: Optional list of output sockets to add to the node tree.

        Returns:
        - The created shader node tree.
        """
        # new() is declared as returning the NodeTree base class; the second argument is the
        # bl_idname of the subclass it actually makes.
        node_tree = typing.cast(bpy.types.ShaderNodeTree, bpy.data.node_groups.new(node_tree_name, 'ShaderNodeTree'))
        return node_tree

    @staticmethod
    def destroy_node_tree(node_tree: bpy.types.NodeTree) -> None:
        """
        Remove the specified shader node tree from Blender's data.

        Parameters:
        - node_tree: The shader node tree to be removed.
        """
        bpy.data.node_groups.remove(node_tree)

    @staticmethod
    def ensure_v2_node_groups_exist(fail_on_validation: bool = False) -> None:
        """Iterate over all v2 node groups and check them, creating them if they haven't been initialized."""
        from ..entities.nodemodel.v2 import COMPOSITE_NODE_WRAPPERS
        for group_name in COMPOSITE_NODE_WRAPPERS.keys():
            group = COMPOSITE_NODE_WRAPPERS[group_name]
            _LOG.debug("Ensuring group exists", (group_name, group, group.node_class_name))
            group.ensure_exists()

        _LOG.debug("Starting validation")

        for group_name in COMPOSITE_NODE_WRAPPERS.keys():
            group = COMPOSITE_NODE_WRAPPERS[group_name]
            _LOG.debug("Validating", group)
            group.validate_tree_against_original_def(fail_hard=fail_on_validation)

    @staticmethod
    def get_v2_node_info(node: bpy.types.Node) -> NodeInfoV2:
        """Return a model v2 dict with information about a node instance, such as its values for input and output sockets,
        and its attributes."""
        if not node:
            raise ValueError("Cannot get node info about None")
        node_info: NodeInfoV2 = {
            "class": node.__class__.__name__,
            "inputs": dict(),
            "outputs": dict(),
            "attributes": dict(),
            }
        if hasattr(node, "inputs"):
            for input_socket in node.inputs:
                input_dict: dict[str, Any] = dict()
                input_dict["name"] = input_socket.name
                input_dict["identifier"] = input_socket.identifier
                input_dict["class"] = input_socket.__class__.__name__
                input_dict["value_type"] = input_socket.type
                input_dict["default_value"] = None
                # See the note on socket default values at the top of the module.
                valued_input = typing.cast(Any, input_socket)
                if hasattr(input_socket, "default_value") and valued_input.default_value is not None:
                    if "Euler" not in valued_input.default_value.__class__.__name__:  # TODO: Euler is not JSON serializable, need to find workaround
                        if input_socket.type in ["RGBA", "RGB", "VECTOR"]:
                            input_dict["default_value"] = list(valued_input.default_value)
                        else:
                            input_dict["default_value"] = valued_input.default_value
                if "Float" in input_dict["class"] and hasattr(node, "node_tree"):
                    _LOG.debug("input_socket", input_socket)
                    # node_tree is declared only on a group node, which is what the hasattr() above
                    # tests for, and a group node which is in a material always has one. The group
                    # interface therefore carries a socket of this name, and min_value/max_value are
                    # declared on the float subclass rather than on the interface socket base.
                    group_tree = typing.cast(bpy.types.NodeTree, typing.cast(ShaderNodeGroup, node).node_tree)
                    tree_input = typing.cast(bpy.types.NodeTreeInterfaceSocketFloat,
                                             NodeTreeService.get_input_socket(group_tree, input_socket.name))
                    input_dict["min_value"] = tree_input.min_value
                    input_dict["max_value"] = tree_input.max_value
                if not input_dict["class"] in _BLACKLISTED_ATTRIBUTE_TYPES:  # TODO: Should try to parse these instead of filtering them out
                    node_info["inputs"]["Input_Socket_" + input_socket.name] = input_dict
        if hasattr(node, "outputs"):
            for output_socket in node.outputs:
                output_dict: dict[str, Any] = dict()
                output_dict["name"] = output_socket.name
                output_dict["identifier"] = output_socket.identifier
                output_dict["class"] = output_socket.__class__.__name__
                output_dict["value_type"] = output_socket.type
                output_dict["default_value"] = None
                # See the note on socket default values at the top of the module.
                valued_output = typing.cast(Any, output_socket)
                if hasattr(output_socket, "default_value") and valued_output.default_value is not None:
                    if "Euler" not in valued_output.default_value.__class__.__name__:  # TODO: Euler is not JSON serializable, need to find workaround
                        if output_socket.type in ["RGBA", "RGB", "VECTOR"]:
                            output_dict["default_value"] = list(valued_output.default_value)
                        else:
                            output_dict["default_value"] = valued_output.default_value
                if not output_dict["class"] in _BLACKLISTED_ATTRIBUTE_TYPES:  # TODO: Should try to parse these instead of filtering them out
                    node_info["outputs"]["Output_Socket_" + output_socket.name] = output_dict
        for item in dir(node):
            if not item in _INTERNAL_NODE_CLASS_ATTRIBUTES and not item in _BLACKLISTED_NODE_CLASS_ATTRIBUTES:
                attribute: dict[str, Any] = dict()
                attribute["name"] = item
                value = getattr(node, item)
                value_type = type(value)
                attribute["class"] = value_type.__name__
                attribute["value"] = value
                if attribute["class"] == "str" and attribute["value"].isupper():
                    attribute["class"] = "enum"
                if attribute["class"] in ["Color", "Vector"]:
                    attribute["value"] = []
                    for i in value:
                        attribute["value"].append(i)
                if not attribute["class"] in _BLACKLISTED_ATTRIBUTE_TYPES:  # TODO: Should try to parse these instead of filtering them out
                    node_info["attributes"][item] = attribute
                if attribute["name"] == "image":  # Special case for shadernodeteximage
                    attribute["class"] = "image"
                    attribute["value"] = dict()
                    attribute["value"]["filepath"] = ""
                    attribute["value"]["colorspace"] = "sRGB"
                    # Only ShaderNodeTexImage declares an image, and the branch is entered on the
                    # name of that very attribute.
                    image_node = typing.cast(bpy.types.ShaderNodeTexImage, node)
                    if image_node.image:
                        fp = NodeService.get_image_file_path(image_node)
                        if fp:
                            attribute["value"]["filepath"] = fp
                        if image_node.image.colorspace_settings and image_node.image.colorspace_settings.name:
                            attribute["value"]["colorspace"] = image_node.image.colorspace_settings.name

        return node_info

    @staticmethod
    def get_known_shader_node_classes() -> list[type[bpy.types.ShaderNode]]:
        """
        Retrieve a list of known shader node classes.

        Returns:
        - A list of the classes themselves, not their names: every class in bpy.types which has
          bpy.types.ShaderNode as a direct base.
        """
        return list(_KNOWN_SHADER_NODE_CLASSES)

    @staticmethod
    def get_node_info(node: bpy.types.Node) -> NodeInfo:
        """Return a model v1 dict with information about a node instance, such as its input and output sockets,
        its class and its attributes."""

        _LOG.enter()
        _LOG.dump("node", node)
        node_info: NodeInfo = dict()
        node_info["type"] = node.__class__.__name__
        node_info["name"] = node.name
        node_info["label"] = node.label
        # mathutils.Vector declares neither __iter__ nor __len__ in the stubs although both work
        # at runtime, so it is read through a sequence cast.
        node_info["location"] = list(typing.cast("typing.Sequence[float]", node.location))
        node_info["create"] = True
        values: SocketValues = dict()
        if hasattr(node, "inputs"):
            for node_input in node.inputs:
                _LOG.dump("node_input", node_input)
                if node_input.__class__.__name__ in ["NodeSocketColor", "NodeSocketFloatFactor", "NodeSocketFloat"]:
                    if isinstance(node_input, NodeSocketColor):
                        # bpy_prop_array declares neither __iter__ nor __getitem__, although both
                        # work at runtime, so a colour is read through a sequence cast.
                        values[node_input.name] = list(typing.cast("typing.Sequence[float]", node_input.default_value))
                    else:
                        # The class name test above leaves only the two float socket classes here.
                        values[node_input.name] = typing.cast(bpy.types.NodeSocketFloat, node_input).default_value
        node_info["values"] = values
        if node_info["type"] == "ShaderNodeTexImage":
            NodeService._add_tex_image_info(typing.cast(bpy.types.ShaderNodeTexImage, node), node_info)
        # The four branches below each read a property declared on the subclass their own class name
        # test has just established, so each one casts to that subclass.
        if node_info["type"] == "ShaderNodeMath":
            math_node = typing.cast(bpy.types.ShaderNodeMath, node)
            node_info["operation"] = math_node.operation
            node_info["use_clamp"] = math_node.use_clamp
        if node_info["type"] == "ShaderNodeVectorMath":
            node_info["operation"] = typing.cast(bpy.types.ShaderNodeVectorMath, node).operation
        if node_info["type"] == "ShaderNodeValue":
            node_info["value"] = typing.cast(bpy.types.NodeSocketFloat, node.outputs[0]).default_value
        return node_info

    @staticmethod
    def get_socket_default_values(node: bpy.types.Node) -> SocketValues:
        """Return a dict with the default values of all input sockets for a node."""
        _LOG.enter()
        values: SocketValues = dict()
        if hasattr(node, "inputs"):
            for node_input in node.inputs:
                _LOG.dump("node_input", node_input)
                if node_input.__class__.__name__ in ["NodeSocketColor", "NodeSocketFloatFactor", "NodeSocketFloat"]:
                    if isinstance(node_input, NodeSocketColor):
                        # See the colour note in get_node_info().
                        values[node_input.name] = list(typing.cast("typing.Sequence[float]", node_input.default_value))
                    else:
                        values[node_input.name] = typing.cast(bpy.types.NodeSocketFloat, node_input).default_value
        else:
            _LOG.debug("Node did not have the inputs attribute")

        return values

    @staticmethod
    def set_socket_default_values(node: bpy.types.Node, values: SocketValues) -> None:
        """Set the node's input socket default values to the values provided in the "values" dict."""
        _LOG.enter()
        if hasattr(node, "inputs"):
            for node_input in node.inputs:
                _LOG.dump("node_input", node_input)
                if node_input.__class__.__name__ in ["NodeSocketColor", "NodeSocketFloatFactor", "NodeSocketFloat"] and node_input.name in values:
                    # A write has no cast form which satisfies bpy_prop_array for the colour case,
                    # and the value is a float for the other two classes, so this is one Any for the
                    # three socket classes the test above admits.
                    typing.cast(Any, node_input).default_value = values[node_input.name]
        else:
            _LOG.debug("Node did not have the inputs attribute")

    @staticmethod
    def _add_tex_image_info(node: bpy.types.ShaderNodeTexImage, node_info: NodeInfo) -> None:
        node_info["colorspace"] = "sRGB"
        if node.image and node.image.colorspace_settings:
            node_info["colorspace"] = node.image.colorspace_settings.name
        node_info["filename"] = NodeService.get_image_file_path(node)

    @staticmethod
    def get_link_info(link: bpy.types.NodeLink) -> LinkInfo:
        """Return a dict with information about a specific node link, ie a connection between one node's output
        socket and another node's input socket. The dict will contain info about both participating nodes and
        participating sockets."""

        _LOG.enter()

        # All four endpoints of a NodeLink are declared optional, and the RNA agrees: none of them
        # is marked never-null on either supported blender. A link which is actually in a tree's
        # links collection always has all four, though, which is the only way one gets here, so the
        # four are narrowed once rather than tested fourteen times.
        from_node = typing.cast(bpy.types.Node, link.from_node)
        to_node = typing.cast(bpy.types.Node, link.to_node)
        from_socket = typing.cast(bpy.types.NodeSocket, link.from_socket)
        to_socket = typing.cast(bpy.types.NodeSocket, link.to_socket)

        link_info: LinkInfo = dict()
        link_info["from_node"] = from_node.name
        link_info["to_node"] = to_node.name

        name_appears_multiple_times_in_from_node = False
        socket_output_number = 0
        current_output_number = 0
        for output in from_node.outputs:
            _LOG.dump("socket:", (output, from_socket, output == from_socket))
            if output == from_socket:
                socket_output_number = current_output_number
            if output != from_socket and output.name == from_socket.name:
                name_appears_multiple_times_in_from_node = True
            current_output_number = current_output_number + 1

        name_appears_multiple_times_in_to_node = False
        socket_input_number = 0
        current_input_number = 0
        for inp in to_node.inputs:
            if inp == to_socket:
                socket_input_number = current_input_number
            if inp != to_socket and inp.name == to_socket.name:
                name_appears_multiple_times_in_to_node = True
            current_input_number = current_input_number + 1

        if name_appears_multiple_times_in_from_node:
            _LOG.trace("Node with multiple output sockets of the same name", (from_node, from_socket.name))
            link_info["from_socket"] = socket_output_number
        else:
            link_info["from_socket"] = from_socket.name

        if name_appears_multiple_times_in_to_node:
            _LOG.trace("Node with multiple input sockets of the same name", (to_node, to_socket.name))
            link_info["to_socket"] = socket_input_number
        else:
            link_info["to_socket"] = to_socket.name

        if name_appears_multiple_times_in_from_node or name_appears_multiple_times_in_to_node:
            _LOG.dump("Multiple sockets of same name", (to_node, to_socket.name, link_info))

        return link_info

    @staticmethod
    def get_node_tree_as_dict(node_tree: bpy.types.NodeTree, recurse_groups: bool = True,
                              group_dict: dict[str, NodeTreeDict] | None = None, recursion_level: int = 0) -> NodeTreeDict:
        """Return a dict describing an entire node tree, including node definitions, groups and links.
        Do not provide a value for recursion level manually, it is used when recursing into
        nested node groups."""

        _LOG.enter()
        _LOG.dump("node_tree", node_tree)

        for_output: NodeTreeDict = dict()
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
                # A group node in a tree being serialised always refers to a tree; an empty one
                # could only come from a group node added by hand and never assigned.
                group_tree = typing.cast(bpy.types.ShaderNodeTree, node.node_tree)
                group_name = group_tree.name
                for_output["nodes"][name]["group_name"] = group_name
                if group_name not in group_dict:
                    if not recurse_groups:
                        group_dict[group_name] = dict()
                    else:
                        group_dict[group_name] = NodeService.get_node_tree_as_dict(
                            group_tree,
                            recurse_groups=True,
                            group_dict=group_dict,
                            recursion_level=recursion_level + 1)
                group_dict[group_name]["inputs"] = {}
                group_dict[group_name]["outputs"] = {}
                # NodeTree.inputs and NodeTree.outputs do not exist. Blender replaced them with
                # NodeTree.interface in 4.0, two minor versions before this addon's own floor, and
                # both reads below raise AttributeError on every supported version -- verified on
                # 4.2.1 and on 5.1, where neither name appears in NodeTree.bl_rna.properties. So
                # this whole block is dead and the method cannot serialise a tree which contains a
                # group node at all. NodeTreeService.get_socket() walks interface.items_tree, which
                # is the form that works, and the three statements below would have to be rewritten
                # against it. That is a logic change rather than an annotation, so it is left as it
                # stands; the ignores below exist to record it, not to excuse it.
                for input_socket in group_tree.inputs:  # pyright: ignore[reportAttributeAccessIssue]
                    group_dict[group_name]["inputs"][input_socket.name] = dict()
                    group_dict[group_name]["inputs"][input_socket.name]["type"] = _NODETYPETOCLASS[input_socket.type]
                    value = typing.cast(Any, node.inputs.get(input_socket.name)).default_value
                    if input_socket.type == "RGBA":
                        value = [value[0], value[1], value[2], value[3]]
                    if input_socket.type != "VECTOR":
                        group_dict[group_name]["inputs"][input_socket.name]["value"] = value
                for output_socket in group_tree.outputs:  # pyright: ignore[reportAttributeAccessIssue]
                    group_dict[group_name]["outputs"][output_socket.name] = _NODETYPETOCLASS[output_socket.type]

        links = node_tree.links

        for link in links:
            for_output["links"].append(NodeService.get_link_info(link))

        _LOG.dump("nodes", for_output)
        return for_output

    @staticmethod
    def clear_node_tree(node_tree: bpy.types.NodeTree, also_destroy_groups: bool = False) -> None:
        """Delete all nodes in a node tree. The tree instance as such will be preserved."""
        nodes: list[bpy.types.Node] = []
        for node in node_tree.nodes:
            _LOG.debug("Node", (node, isinstance(node, ShaderNodeGroup)))
            nodes.append(node)
            if also_destroy_groups and isinstance(node, ShaderNodeGroup):
                # A group node with no tree has nothing to rename, and the log line below would be
                # the first to fail on one. See the note in get_node_tree_as_dict().
                group_tree = typing.cast(bpy.types.ShaderNodeTree, node.node_tree)
                _LOG.debug("found group to destroy", (node, node.name, group_tree, group_tree.name))
                node.name = node.name + ".unused"
                group_tree.name = group_tree.name + ".unused"
        for node in nodes:
            node_tree.nodes.remove(node)

    @staticmethod
    def set_image_in_image_node(node: bpy.types.ShaderNodeTexImage, file_name: str, colorspace: str | None = None) -> None:
        """Update an existing image node with the provided filename and colorspace."""
        if not file_name or not str(file_name).strip():
            _LOG.warn("Trying to load image with null/empty filename")
            return
        bn = os.path.basename(file_name)
        image: bpy.types.Image
        if bn in bpy.data.images:
            _LOG.debug("image existed:", bn)
            image = bpy.data.images[bn]
        else:
            _LOG.debug("Will attempt to load file", file_name)
            if os.path.exists(file_name):
                image = bpy.data.images.load(file_name)
                _LOG.debug("Image after loading file", image)
            else:
                _LOG.error("File does not exist:", file_name)
                return
        # Image.colorspace_settings cannot be None: it is an embedded struct rather than a pointer,
        # so there is nothing for it to be null for -- which is why the else branch of the code's
        # own test below can never run. The RNA enum behind its name carries only "NONE"
        # statically, because the real colorspace list is populated from OCIO at runtime, so no
        # stub can know the name an asset asks for.
        colorspace_settings = typing.cast(bpy.types.ColorManagedInputColorspaceSettings, image.colorspace_settings)
        if colorspace:
            try:
                colorspace_settings.name = colorspace  # pyright: ignore[reportAttributeAccessIssue]
            except TypeError as e:
                _LOG.error("Tried to set color space \"" + colorspace + "\" but blender says", e)
                if colorspace_settings:
                    _LOG.error("Image colorspace defaults to", colorspace_settings.name)
                else:
                    _LOG.error("Image does not have any colorspace settings")
        else:
            colorspace_settings.name = "sRGB"  # pyright: ignore[reportAttributeAccessIssue]
        node.image = image

    @staticmethod
    def update_tex_image_with_settings_from_dict(node: bpy.types.ShaderNodeTexImage, node_info: NodeInfo) -> None:
        """Set file name and colorspace information in an image texture node based on
        information in the provided dict. This will also load the file as an
        image object if this had not already been done."""

        file_name = node_info["filename"]
        colorspace = None

        if "colorspace" in node_info:
            colorspace = node_info["colorspace"]

        NodeService.set_image_in_image_node(node, file_name, colorspace)

    @staticmethod
    def update_node_with_settings_from_dict(node: bpy.types.Node, node_info: NodeInfo) -> None:
        """Set node attributes and input socket default values based on information
        in the provided dict."""

        # Every branch below reads or writes a property declared on the subclass its own
        # node_info["type"] test has just established, so each one casts to that subclass.
        if node_info["type"] == "ShaderNodeGroup":
            if "group_name" in node_info:
                group_name = node_info["group_name"]
            else:
                group_name = node_info["name"]
            if not group_name in bpy.data.node_groups:
                _LOG.error("Tried to assign a node tree which did not exist", node_info)
                raise ValueError("Tried to assign a node tree which did not exist")
            typing.cast(ShaderNodeGroup, node).node_tree = typing.cast(bpy.types.ShaderNodeTree, bpy.data.node_groups.get(group_name))

        if "location" in node_info:
            node.location = node_info["location"]

        if node_info["type"] == "ShaderNodeTexImage":
            NodeService.update_tex_image_with_settings_from_dict(typing.cast(bpy.types.ShaderNodeTexImage, node), node_info)

        if node_info["type"] in ["ShaderNodeMix", "ShaderNodeMixRGB"] and "blend_type" in node_info:
            typing.cast(bpy.types.ShaderNodeMixRGB, node).blend_type = node_info["blend_type"]

        if node_info["type"] in ["ShaderNodeMath", "ShaderNodeVectorMath"]:
            # ShaderNodeVectorMath has no use_clamp, so the second write is for the maths node only;
            # a vector maths entry carrying one would be an AttributeError.
            math_node = typing.cast(bpy.types.ShaderNodeMath, node)
            if "operation" in node_info:
                math_node.operation = node_info["operation"]
            if "use_clamp" in node_info:
                math_node.use_clamp = node_info["use_clamp"]

        if node_info["type"] == "ShaderNodeValToRGB" and "stops" in node_info:
            # color_ramp is declared Optional but is an embedded struct on the node, so a
            # ShaderNodeValToRGB always has one.
            color_ramp = typing.cast(bpy.types.ColorRamp, typing.cast(bpy.types.ShaderNodeValToRGB, node).color_ramp)
            elements = color_ramp.elements
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
            typing.cast(bpy.types.NodeSocketFloat, node.outputs[0]).default_value = node_info["value"]

        for value in node_info["values"]:
            if not value in node.inputs:
                _LOG.error("Found an input name which didn't exist as socket:", value)
                sockets = []
                for inp in node.inputs:
                    sockets.append((inp.name, inp.type))
                _LOG.error("The following input sockets exist on node", (node, sockets))
            else:
                try:
                    # See the note on socket default values at the top of the module. A write has no
                    # cast form for the colour case, and the dict carries values for every socket
                    # class a template may name, so this is one Any rather than a per class branch.
                    typing.cast(Any, node.inputs[value]).default_value = node_info["values"][value]
                except ValueError as e:
                    _LOG.error("Tried to set illegal default value", {
                        "node": node,
                        "input name": value,
                        "input": node.inputs[value],
                        "value": node_info["values"][value],
                        "error": e
                        })
        node.name = node_info["name"]
        if "label" in node_info:
            node.label = node_info["label"]

    @staticmethod
    def _ensure_group_interfaces_exist(dict_with_node_tree: NodeTreeDict, force_wipe_group_node_trees: bool = False) -> None:
        _LOG.enter()
        if not "groups" in dict_with_node_tree or not dict_with_node_tree["groups"]:
            _LOG.debug("The node tree dict did not have a group definition hierarchy")
            return

        groups = dict_with_node_tree["groups"]
        for group_name in groups.keys():
            group = groups[group_name]
            group["pre_existing"] = False
            _LOG.debug("Starting to analyze group", group_name)
            node_tree: bpy.types.NodeTree
            if group_name in bpy.data.node_groups:
                # The membership test above is what makes get() non-empty.
                node_tree = typing.cast(bpy.types.NodeTree, bpy.data.node_groups.get(group_name))
                if force_wipe_group_node_trees:
                    _LOG.warn("Wiping node tree", group_name)
                    NodeService.clear_node_tree(node_tree)
                else:
                    group["pre_existing"] = True
            else:
                node_tree = bpy.data.node_groups.new(group_name, type="ShaderNodeTree")

            input_node: bpy.types.Node | None = None
            output_node: bpy.types.Node | None = None

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
                    if not NodeService._has_socket(node_tree, input_name, in_out="INPUT"):
                        input_def = group["inputs"][input_name]
                        _LOG.debug("Missing input socket:", input_def)
                        create = True
                        if "create" in input_def:
                            create = input_def["create"]
                        if create:
                            input_socket = NodeService._create_socket(node_tree, input_name, input_def["type"], in_out="INPUT")
                            _LOG.debug("Input socket created:", input_socket)
                            if not "Vector" in input_def["type"]:
                                # NodeTreeInterfaceSocket declares no default_value either; it is on
                                # each concrete interface socket subclass, and the type string in the
                                # template decides which one this is. One Any for the same reason as
                                # the node socket writes above.
                                typing.cast(Any, input_socket).default_value = input_def["value"]
                    else:
                        _LOG.debug("Input socket already existed:", input_name)

            if "outputs" in group:
                for output_name in group["outputs"].keys():
                    if not NodeService._has_socket(node_tree, output_name, in_out="OUTPUT"):
                        _LOG.debug("Missing output socket:", output_name)
                        socket = NodeService._create_socket(node_tree, output_name, group["outputs"][output_name], in_out="OUTPUT")
                        _LOG.debug("Output socket created:", socket)
                    else:
                        _LOG.debug("Output socket already existed:", output_name)

    @staticmethod
    def _has_socket(node_tree: bpy.types.NodeTree, socket_name: str, in_out: SocketInOut = "INPUT") -> bool:
        """Private duplicate of NodeTreeService.has_socket(), kept because it predates that service."""
        _LOG.enter()
        # NodeTree.interface cannot be None: it is an embedded struct on the tree rather than a
        # pointer. NodeTreeService says the same at its own reads.
        for item in typing.cast(bpy.types.NodeTreeInterface, node_tree.interface).items_tree:
            if isinstance(item, bpy.types.NodeTreeInterfaceSocket):
                if item.in_out == in_out:
                    if item.name == socket_name:
                        return True
        return False

    @staticmethod
    def _create_socket(node_tree: bpy.types.NodeTree, socket_name: str, socket_type: str,
                       in_out: SocketInOut = "INPUT") -> bpy.types.NodeTreeInterfaceSocket:
        """Private duplicate of NodeTreeService.create_socket(), kept because it predates that service."""
        _LOG.enter()
        # interface is never None, see _has_socket(). socket_type is the bl_idname of a socket
        # class, for example "NodeSocketFloat", where the stubs declare the parameter as
        # Literal["DEFAULT"] -- the sole value the RNA enum carries statically, so every real
        # argument fails the check.
        interface = typing.cast(bpy.types.NodeTreeInterface, node_tree.interface)
        return interface.new_socket(socket_name, socket_type=socket_type, in_out=in_out)  # pyright: ignore[reportArgumentType]

    @staticmethod
    def apply_node_tree_from_dict(target_node_tree: bpy.types.NodeTree, dict_with_node_tree: NodeTreeDict,
                                  wipe_node_tree: bool = False) -> None:
        """Update an entire node tree based on information in the provided dict. The node tree
        must exist. This will also recursively update or create node groups if necessary."""

        _LOG.enter()

        if wipe_node_tree:
            NodeService.clear_node_tree(target_node_tree)

        NodeService._ensure_group_interfaces_exist(dict_with_node_tree)

        node_by_name: dict[str, bpy.types.Node | None] = dict()

        if "groups" in dict_with_node_tree:
            groups = dict_with_node_tree["groups"]
            for group_name in groups.keys():
                group = groups[group_name]
                if not "pre_existing" in group or not group["pre_existing"]:
                    if group_name in bpy.data.node_groups:
                        # The membership test above is what makes get() non-empty.
                        node_tree = typing.cast(bpy.types.NodeTree, bpy.data.node_groups.get(group_name))
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
                    # Narrowed by the raise above; the subscript is re-read, which pyright cannot
                    # narrow through for a non literal key.
                    NodeService.update_node_with_settings_from_dict(typing.cast(bpy.types.Node, node_by_name[node_name]), node_info)
                else:
                    new_node = NodeService.create_node_from_dict(target_node_tree, node_info)
                    _LOG.dump("Created node", new_node)
                    node_by_name[node_name] = new_node
            else:
                _LOG.dump("Not creating node", node_info)

        links = target_node_tree.links

        for link in dict_with_node_tree["links"]:
            if link["from_node"] in node_by_name and link["to_node"] in node_by_name:
                if "disabled" in link and link["disabled"]:
                    continue
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
    def get_or_create_node_group(group_name: str) -> bpy.types.ShaderNodeTree:
        """Find a node tree with the given group name and return it. If it doesn't exist, then create it."""
        if group_name in bpy.data.node_groups:
            # The membership test is what makes get() non-empty, and the type argument below is what
            # makes the new tree a ShaderNodeTree. A pre-existing group of another tree type would
            # not in fact be one, but nothing in MPFB makes a node group which is not a shader tree.
            return typing.cast(bpy.types.ShaderNodeTree, bpy.data.node_groups.get(group_name))
        return typing.cast(bpy.types.ShaderNodeTree, bpy.data.node_groups.new(group_name, type="ShaderNodeTree"))

    @staticmethod
    def find_node_by_name(node_tree: bpy.types.NodeTree, node_name: str) -> bpy.types.Node | None:
        """Find a node with the given name in the node tree."""
        _LOG.enter()
        for node in node_tree.nodes:
            if node.name == node_name:
                return node
        return None

    @staticmethod
    def find_nodes_by_type_name(node_tree: bpy.types.NodeTree, type_name: str) -> list[bpy.types.Node]:
        """Return an array with all nodes of the given type in the node tree."""
        _LOG.enter()
        nodes: list[bpy.types.Node] = []
        for node in node_tree.nodes:
            _LOG.debug("node", node)
            _LOG.debug("node.type", node.type)
            _LOG.debug("node class", node.__class__.__name__)
            if type_name in [node.__class__.__name__, node.type]:
                nodes.append(node)
        return nodes

    @staticmethod
    def find_input_socket_by_identifier_or_name(node: bpy.types.Node, socket_identifier: str, socket_name: str | None = None,
                                                force_find_by_name: bool = False) -> bpy.types.NodeSocket | None:
        """Return the input socket with the given identifier or name. If the socket is not found, return None."""
        _LOG.enter()
        return NodeService._find_socket_by_identifier_or_name(node, node.inputs, socket_identifier, socket_name, force_find_by_name)

    @staticmethod
    def find_output_socket_by_identifier_or_name(node: bpy.types.Node, socket_identifier: str, socket_name: str | None = None,
                                                 force_find_by_name: bool = False) -> bpy.types.NodeSocket | None:
        """Return the output socket with the given identifier or name. If the socket is not found, return None."""
        _LOG.enter()
        return NodeService._find_socket_by_identifier_or_name(node, node.outputs, socket_identifier, socket_name, force_find_by_name)

    @staticmethod
    def _find_socket_by_identifier_or_name(node: bpy.types.Node, sockets: typing.Iterable[bpy.types.NodeSocket],
                                           socket_identifier: str, socket_name: str | None = None,
                                           force_find_by_name: bool = False) -> bpy.types.NodeSocket | None:
        """Return the a socket with the given identifier or name. If the socket is not found, return None."""
        _LOG.enter()
        _LOG.debug("Sockets", sockets)
        if not socket_name and force_find_by_name:
            _LOG.error("Illegal combination", (socket_name, force_find_by_name))
            raise ValueError('Tried to force find a socket by name, but no socket name was provided')
        _LOG.debug("Node", node)
        if node.__class__.__name__ == "ShaderNodeGroup" and socket_name:
            # Prefer name over identifier if we are operating on a group
            _LOG.debug("Is group and name is provided")
            for socket in sockets:
                _LOG.debug("Socket", socket)
                if socket.name == socket_name:
                    _LOG.debug("Socket match for group", socket)
                    return socket
        if socket_identifier and not force_find_by_name:
            _LOG.debug("Searching for socket by identifier", socket_identifier)
            for socket in sockets:
                _LOG.debug("Socket", socket)
                if socket.identifier == socket_identifier:
                    _LOG.debug("Socket match for identifier", socket)
                    return socket
        _LOG.debug("Searching for socket by name", socket_name)
        for socket in sockets:
            _LOG.debug("Socket", socket)
            if socket.name == socket_name:
                _LOG.debug("Socket match for name", socket)
                return socket
        _LOG.warn("Did not find socket", (node, sockets, socket_identifier, socket_name))
        return None

    @staticmethod
    def find_first_node_by_type_name(node_tree: bpy.types.NodeTree, type_name: str) -> bpy.types.Node | None:
        """Find the first node with the given type in the node tree."""
        _LOG.enter()
        nodes = NodeService.find_nodes_by_type_name(node_tree, type_name)
        if nodes is None or len(nodes) < 1:
            _LOG.debug("Got an empty list of nodes for type", type_name)
            return None
        return nodes[0]

    @staticmethod
    def find_first_group_node_by_tree_name(node_tree: bpy.types.NodeTree, tree_name: str) -> ShaderNodeGroup | None:
        """Find the first ShaderNodeGroup with the indicated node tree."""
        _LOG.enter()
        nodes = NodeService.find_nodes_by_type_name(node_tree, "ShaderNodeGroup")
        if nodes is None or len(nodes) < 1:
            _LOG.debug("Got an empty list of group nodes")
            return None
        for node in nodes:
            # The search was by class name, so every hit is a group node, and a group node in a
            # material always refers to a tree. See the note in get_node_tree_as_dict().
            group_node = typing.cast(ShaderNodeGroup, node)
            if typing.cast(bpy.types.ShaderNodeTree, group_node.node_tree).name == tree_name:
                return group_node
        return None

    @staticmethod
    def find_nodes_by_class(node_tree: bpy.types.NodeTree, type_class: type) -> list[bpy.types.Node]:
        """Return an array with all nodes of the given type class in the node tree."""
        _LOG.enter()
        nodes: list[bpy.types.Node] = []
        for node in node_tree.nodes:
            if isinstance(node, type_class):
                nodes.append(node)
        return nodes

    @staticmethod
    def find_first_node_by_class(node_tree: bpy.types.NodeTree, type_class: type) -> bpy.types.Node | None:
        """Find the first node with the given type class in the node tree."""
        _LOG.enter()
        nodes = NodeService.find_nodes_by_class(node_tree, type_class)
        if nodes is None or len(nodes) < 1:
            return None
        return nodes[0]

    @staticmethod
    def find_socket_default_value(node: bpy.types.Node, socket_name: str) -> Any:
        """Return the default value of the node's input socket with the given name.

        The return is Any because it is whatever the socket class holds: a float, a bool, a string
        or a colour, depending entirely on which socket was asked for. None is also a genuine
        answer, for a node with no inputs or no input of that name."""
        _LOG.enter()
        if not node:
            raise ValueError('Cannot find values on None node')
        if not node.inputs:
            _LOG.error("Node of type " + str(type(node)) + " didn't have any inputs!?")
            return None
        if not socket_name in node.inputs:
            _LOG.warn("Node of type " + str(type(node)) + " didn't have any input called ", socket_name)
            return None
        # See the note on socket default values at the top of the module. Any, not a subclass,
        # because the caller names the socket and so decides what comes back.
        return typing.cast(Any, node.inputs[socket_name]).default_value

    @staticmethod
    def find_node_linked_to_socket(node_tree: bpy.types.NodeTree, node_which_is_linked_to: bpy.types.Node,
                                   name_of_socket: str) -> bpy.types.Node | None:
        """Return the node that links to an input socket in the given node."""
        _LOG.enter()
        if not node_which_is_linked_to or not name_of_socket:
            raise ValueError('Cannot find values on None node or socket')
        source_side_of_link: bpy.types.Node | None = None
        _LOG.debug("Looking for node linked to socket", (node_which_is_linked_to, name_of_socket))
        for link in node_tree.links:
            # The four endpoints of a link in a tree are never empty; see the note in
            # get_link_info().
            link_from_node = typing.cast(bpy.types.Node, link.from_node)
            link_to_node = typing.cast(bpy.types.Node, link.to_node)
            link_to_socket = typing.cast(bpy.types.NodeSocket, link.to_socket)
            _LOG.debug("-- Link", {
                "from_node": link_from_node.name,
                "to_node": link_to_node.name,
                "from_socket": typing.cast(bpy.types.NodeSocket, link.from_socket).name,
                "to_socket": link_to_socket.name})
            if link_to_node.name == node_which_is_linked_to.name:
                _LOG.debug("Found link to correct node")
                if link_to_socket.name == name_of_socket:
                    source_side_of_link = link_from_node
                    _LOG.debug("Found linking node", source_side_of_link)
                    break
                else:
                    _LOG.debug("Socket name does not match", (link_to_socket.name, name_of_socket))
        return source_side_of_link

    @staticmethod
    def remove_link(node_tree: bpy.types.NodeTree, node_which_is_linked_to: bpy.types.Node, name_of_socket: str) -> None:
        """Remove a link that links to an input socket in the given node, if any"""
        _LOG.enter()
        if not node_which_is_linked_to or not name_of_socket:
            raise ValueError('Cannot find values on None node or socket')
        _LOG.debug("Looking for node linked to socket", (node_which_is_linked_to, name_of_socket))
        for link in node_tree.links:
            # The four endpoints of a link in a tree are never empty; see the note in
            # get_link_info().
            link_from_node = typing.cast(bpy.types.Node, link.from_node)
            link_to_node = typing.cast(bpy.types.Node, link.to_node)
            link_to_socket = typing.cast(bpy.types.NodeSocket, link.to_socket)
            _LOG.debug("-- Link", {
                "from_node": link_from_node.name,
                "to_node": link_to_node.name,
                "from_socket": typing.cast(bpy.types.NodeSocket, link.from_socket).name,
                "to_socket": link_to_socket.name})
            if link_to_node.name == node_which_is_linked_to.name:
                _LOG.debug("Found link to correct node")
                if link_to_socket.name == name_of_socket:
                    source_side_of_link = link_from_node
                    _LOG.debug("Found linking node", source_side_of_link)
                    node_tree.links.remove(link)
                    break
                else:
                    _LOG.debug("Socket name does not match", (link_to_socket.name, name_of_socket))

    @staticmethod
    def add_link(node_tree: bpy.types.NodeTree, from_node: bpy.types.Node, to_node: bpy.types.Node,
                 from_socket_name: str, to_socket_name: str) -> None:
        """Add a link between two nodes.

        Neither socket name is checked. A name which does not exist on its node is looked up as
        None and handed to links.new() as one, which raises TypeError rather than reporting which
        of the two names was wrong."""
        _LOG.enter()
        _LOG.debug("Creating link", {
            "from_node": from_node.name,
            "to_node": to_node.name,
            "from_socket": from_socket_name,
            "to_socket": to_socket_name
            })
        from_socket = NodeService.find_output_socket_by_identifier_or_name(from_node, from_socket_name, from_socket_name)
        to_socket = NodeService.find_input_socket_by_identifier_or_name(to_node, to_socket_name, to_socket_name)
        _LOG.debug("Creating link", {
            "from_socket": from_socket,
            "to_socket": to_socket
            })
        # The two finders return None for a socket name which does not exist, and nothing here
        # tests for it; see the docstring.
        node_tree.links.new(typing.cast(bpy.types.NodeSocket, from_socket), typing.cast(bpy.types.NodeSocket, to_socket))

    @staticmethod
    def get_image_file_path(image_texture_node: bpy.types.ShaderNodeTexImage) -> str | None:
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
    def create_node(node_tree: bpy.types.NodeTree, type_name: str, name: str | None = None, label: str | None = None,
                    xpos: float = 0, ypos: float = 0) -> bpy.types.Node:
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
    def create_node_from_dict(node_tree: bpy.types.NodeTree, node_info: NodeInfo) -> bpy.types.Node:
        """Create a new node based on information in the provided dict."""
        new_node = node_tree.nodes.new(node_info["type"])
        NodeService.update_node_with_settings_from_dict(new_node, node_info)
        return new_node

    @staticmethod
    def create_principled_node(node_tree: bpy.types.NodeTree, name: str | None = None, label: str | None = None,
                               xpos: float = 0, ypos: float = 0) -> bpy.types.ShaderNodeBsdfPrincipled:
        """Create a new principled node."""
        _LOG.enter()
        # create_node() returns the Node base class; the type name decides the subclass.
        return typing.cast(bpy.types.ShaderNodeBsdfPrincipled,
                           NodeService.create_node(node_tree, "ShaderNodeBsdfPrincipled", name=name, label=label, xpos=xpos, ypos=ypos))

    @staticmethod
    def create_bump_node(node_tree: bpy.types.NodeTree, name: str | None = None, label: str | None = None,
                         xpos: float = 0, ypos: float = 0) -> bpy.types.ShaderNodeBump:
        """Create a new bump node."""
        _LOG.enter()
        # create_node() returns the Node base class; the type name decides the subclass.
        return typing.cast(bpy.types.ShaderNodeBump,
                           NodeService.create_node(node_tree, "ShaderNodeBump", name=name, label=label, xpos=xpos, ypos=ypos))

    @staticmethod
    def create_normal_map_node(node_tree: bpy.types.NodeTree, name: str | None = None, label: str | None = None,
                               xpos: float = 0, ypos: float = 0) -> bpy.types.ShaderNodeNormalMap:
        """Create a new normal map node."""
        _LOG.enter()
        # create_node() returns the Node base class; the type name decides the subclass.
        return typing.cast(bpy.types.ShaderNodeNormalMap,
                           NodeService.create_node(node_tree, "ShaderNodeNormalMap", name=name, label=label, xpos=xpos, ypos=ypos))

    @staticmethod
    def create_displacement_node(node_tree: bpy.types.NodeTree, name: str | None = None, label: str | None = None,
                                 xpos: float = 0, ypos: float = 0) -> bpy.types.ShaderNodeDisplacement:
        """Create a new displacement map node."""
        _LOG.enter()
        # create_node() returns the Node base class; the type name decides the subclass.
        return typing.cast(bpy.types.ShaderNodeDisplacement,
                           NodeService.create_node(node_tree, "ShaderNodeDisplacement", name=name, label=label, xpos=xpos, ypos=ypos))

    @staticmethod
    def create_mix_rgb_node(node_tree: bpy.types.NodeTree, name: str | None = None, label: str | None = None,
                            xpos: float = 0, ypos: float = 0) -> bpy.types.ShaderNodeMixRGB:
        """Create a new mixrgb node."""
        _LOG.enter()
        # create_node() returns the Node base class; the type name decides the subclass.
        return typing.cast(bpy.types.ShaderNodeMixRGB,
                           NodeService.create_node(node_tree, "ShaderNodeMixRGB", name=name, label=label, xpos=xpos, ypos=ypos))

    @staticmethod
    def create_value_node(node_tree: bpy.types.NodeTree, name: str | None = None, label: str | None = None,
                          xpos: float = 0, ypos: float = 0, default_value: float = 0.0) -> bpy.types.ShaderNodeValue:
        """Create a new value node. The default_value argument is accepted but never applied."""
        _LOG.enter()
        return typing.cast(bpy.types.ShaderNodeValue,
                           NodeService.create_node(node_tree, "ShaderNodeValue", name=name, label=label, xpos=xpos, ypos=ypos))

    @staticmethod
    def create_attibute_node(node_tree: bpy.types.NodeTree, name: str | None = None, label: str | None = None,
                             xpos: float = 0, ypos: float = 0, default_value: str = "") -> bpy.types.ShaderNodeAttribute:
        """Create a new attribute node. The default_value argument is accepted but never applied."""
        _LOG.enter()
        return typing.cast(bpy.types.ShaderNodeAttribute,
                           NodeService.create_node(node_tree, "ShaderNodeAttribute", name=name, label=label, xpos=xpos, ypos=ypos))

    @staticmethod
    def create_image_texture_node(node_tree: bpy.types.NodeTree, name: str | None = None, label: str | None = None,
                                  xpos: float = 0, ypos: float = 0, image_path_absolute: str | None = None,
                                  colorspace: str = "sRGB") -> bpy.types.ShaderNodeTexImage:
        """Create a new image texture node."""
        _LOG.enter()
        new_texture_node = typing.cast(bpy.types.ShaderNodeTexImage,
                                       NodeService.create_node(node_tree, "ShaderNodeTexImage", name=name, label=label, xpos=xpos, ypos=ypos))
        if image_path_absolute:
            image_file_name = os.path.basename(image_path_absolute)
            image: bpy.types.Image
            if image_file_name in bpy.data.images:
                _LOG.debug("image was previously loaded", image_path_absolute)
                image = bpy.data.images[image_file_name]
            else:
                image = bpy.data.images.load(image_path_absolute)
            # See the colorspace note in set_image_in_image_node().
            colorspace_settings = typing.cast(bpy.types.ColorManagedInputColorspaceSettings, image.colorspace_settings)
            colorspace_settings.name = colorspace  # pyright: ignore[reportAttributeAccessIssue]
            new_texture_node.image = image
        return new_texture_node
