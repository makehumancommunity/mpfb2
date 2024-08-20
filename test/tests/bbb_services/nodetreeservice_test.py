import bpy, os, pytest
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodetreeservice import NodeTreeService

def _create_node_tree(node_tree_name):
    node_tree = bpy.data.node_groups.new(node_tree_name, 'ShaderNodeTree')
    return node_tree

def _destroy_node_tree(node_tree):
    bpy.data.node_groups.remove(node_tree)

def test_nodeservice_exists():
    """NodeTreeService"""
    assert NodeTreeService is not None, "NodeTreeService can be imported"

def test_has_input_socket_nonexisting():
    node_tree_name = ObjectService.random_name()
    node_tree = _create_node_tree(node_tree_name)
    assert not NodeTreeService.has_input_socket(node_tree, 'nonexisting')
    _destroy_node_tree(node_tree)

def test_has_output_socket_nonexisting():
    node_tree_name = ObjectService.random_name()
    node_tree = _create_node_tree(node_tree_name)
    assert not NodeTreeService.has_output_socket(node_tree, 'nonexisting')
    _destroy_node_tree(node_tree)

def test_create_input_socket():
    node_tree_name = ObjectService.random_name()
    node_tree = _create_node_tree(node_tree_name)
    socket_name = ObjectService.random_name()
    socket = NodeTreeService.create_input_socket(node_tree, socket_name, "NodeSocketFloat")
    assert socket
    assert socket.name == socket_name
    assert NodeTreeService.has_input_socket(node_tree, socket.name)
    assert not NodeTreeService.has_output_socket(node_tree, socket.name)
    assert NodeTreeService.get_input_socket(node_tree, socket.name)
    assert NodeTreeService.get_input_socket(node_tree, socket.name) == socket
    _destroy_node_tree(node_tree)

def test_create_output_socket():
    node_tree_name = ObjectService.random_name()
    node_tree = _create_node_tree(node_tree_name)
    socket_name = ObjectService.random_name()
    socket = NodeTreeService.create_output_socket(node_tree, socket_name, "NodeSocketFloat")
    assert socket
    assert socket.name == socket_name
    assert NodeTreeService.has_output_socket(node_tree, socket.name)
    assert not NodeTreeService.has_input_socket(node_tree, socket.name)
    assert NodeTreeService.get_output_socket(node_tree, socket.name)
    assert NodeTreeService.get_output_socket(node_tree, socket.name) == socket
    _destroy_node_tree(node_tree)
