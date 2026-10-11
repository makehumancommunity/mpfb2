"""This service provides utility functions for working with blender 4 style shader node trees."""

import bpy
import bpy.types
import typing

from .logservice import LogService

_LOG = LogService.get_logger("services.nodetreeservice")

SocketInOut = typing.Literal["INPUT", "OUTPUT"]

class NodeTreeService:

    """Service with utility functions for working with blender 4 shader node trees. It only has static methods, so you don't
    need to instance it."""

    def __init__(self) -> None:
        """Do not instance, there are only static methods in the class"""
        raise RuntimeError("You should not instance NodeTreeService. Use its static methods instead.")

    @staticmethod
    def get_socket(node_tree: bpy.types.NodeTree, socket_name: str, in_out: SocketInOut = "INPUT") -> bpy.types.NodeTreeInterfaceSocket | None:
        """Return an interface socket with the given name and in/out type, or None if it doesn't exist."""
        _LOG.enter()
        # interface is never None, see the note at the top of the module.
        for item in typing.cast(bpy.types.NodeTreeInterface, node_tree.interface).items_tree:
            _LOG.debug("Item, socket_name", (item, socket_name))
            if isinstance(item, bpy.types.NodeTreeInterfaceSocket):
                if item.in_out == in_out:
                    if item.name == socket_name:
                        _LOG.debug("Returning item", item)
                        return item
                    else:
                        _LOG.debug("Socket name doesn't match", (item.name, socket_name))
                else:
                    _LOG.debug("Socket in_out doesn't match", (item.in_out, in_out))
            else:
                _LOG.debug("Item is not a socket", item)
        return None

    @staticmethod
    def get_output_socket(node_tree: bpy.types.NodeTree, socket_name: str) -> bpy.types.NodeTreeInterfaceSocket | None:
        """Return an interface output socket with the given name, or None if it doesn't exist."""
        _LOG.enter()
        return NodeTreeService.get_socket(node_tree, socket_name, in_out="OUTPUT")

    @staticmethod
    def get_input_socket(node_tree: bpy.types.NodeTree, socket_name: str) -> bpy.types.NodeTreeInterfaceSocket | None:
        """Return an interface input socket with the given name, or None if it doesn't exist."""
        _LOG.enter()
        return NodeTreeService.get_socket(node_tree, socket_name, in_out="INPUT")

    @staticmethod
    def has_socket(node_tree: bpy.types.NodeTree, socket_name: str, in_out: SocketInOut = "INPUT") -> bool:
        """Return True if the given socket exists, False otherwise."""
        _LOG.enter()
        socket = NodeTreeService.get_socket(node_tree, socket_name, in_out=in_out)
        return socket is not None

    @staticmethod
    def has_input_socket(node_tree: bpy.types.NodeTree, socket_name: str) -> bool:
        """Return True if the given input socket exists, False otherwise."""
        _LOG.enter()
        return NodeTreeService.has_socket(node_tree, socket_name, in_out="INPUT")

    @staticmethod
    def has_output_socket(node_tree: bpy.types.NodeTree, socket_name: str) -> bool:
        """Return True if the given output socket exists, False otherwise."""
        _LOG.enter()
        return NodeTreeService.has_socket(node_tree, socket_name, in_out="OUTPUT")

    @staticmethod
    def create_socket(node_tree: bpy.types.NodeTree, socket_name: str, socket_type: str, in_out: SocketInOut = "INPUT") -> bpy.types.NodeTreeInterfaceSocket:
        """Create a new socket with the given name and type, and return it."""
        _LOG.enter()
        # interface is never None, see the note at the top of the module.
        interface = typing.cast(bpy.types.NodeTreeInterface, node_tree.interface)
        # socket_type is the bl_idname of a socket class, for example "NodeSocketFloat". The stubs declare the
        # parameter as Literal["DEFAULT"], which is the sole value the RNA enum carries statically, so every
        # real argument fails the check.
        return interface.new_socket(socket_name, socket_type=socket_type, in_out=in_out)  # pyright: ignore[reportArgumentType]

    @staticmethod
    def create_input_socket(node_tree: bpy.types.NodeTree, socket_name: str, socket_type: str) -> bpy.types.NodeTreeInterfaceSocket:
        """Create a new input socket with the given name and type, and return it."""
        _LOG.enter()
        return NodeTreeService.create_socket(node_tree, socket_name, socket_type, in_out="INPUT")

    @staticmethod
    def create_output_socket(node_tree: bpy.types.NodeTree, socket_name: str, socket_type: str) -> bpy.types.NodeTreeInterfaceSocket:
        """Create a new output socket with the given name and type, and return it."""
        _LOG.enter()
        return NodeTreeService.create_socket(node_tree, socket_name, socket_type, in_out="OUTPUT")
