from mpfb.services.logservice import LogService
from mpfb.entities.nodemodel.atoms import AtomNodeManager

import bpy

_LOG = LogService.get_logger("nodemodel.molecule")
_LOG.set_level(LogService.DEBUG)

_SOCKET_TYPES=[
    "NodeSocketBool",
    "NodeSocketCollection",
    "NodeSocketColor",
    "NodeSocketFloat",
    "NodeSocketFloatAngle",
    "NodeSocketFloatDistance",
    "NodeSocketFloatFactor",
    "NodeSocketFloatPercentage",
    "NodeSocketFloatTime",
    "NodeSocketFloatTimeAbsolute",
    "NodeSocketFloatUnsigned",
    "NodeSocketGeometry",
    "NodeSocketImage",
    "NodeSocketInt",
    "NodeSocketIntFactor",
    "NodeSocketIntPercentage",
    "NodeSocketIntUnsigned",
    "NodeSocketMaterial",
    "NodeSocketObject",
    "NodeSocketShader",
    "NodeSocketString",
    "NodeSocketTexture",
    "NodeSocketVector",
    "NodeSocketVectorAcceleration",
    "NodeSocketVectorDirection",
    "NodeSocketVectorEuler",
    "NodeSocketVectorTranslation",
    "NodeSocketVectorVelocity",
    "NodeSocketVectorXYZ",
    "NodeSocketVirtual"
    ]

class Molecule(AtomNodeManager):

    def __init__(self, group_name, create_duplicate=False):
        _LOG.trace("Constructing Molecule for", group_name)
        self.need_to_create = False
        self.group_name = group_name
        self._get_or_create_node_tree()
        AtomNodeManager.__init__(self, self.group)
        if self.need_to_create:
            self.create_group()

    def _get_or_create_node_tree(self):
        if not self.group_name in bpy.data.node_groups:
            self.group = bpy.data.node_groups.new(self.group_name, type="ShaderNodeTree")
            self.need_to_create = True
        else:
            self.group = bpy.data.node_groups.get(self.group_name)

    def create_group(self):
        raise NotImplemented("This method should be overriden by children")

    def create_input_and_output(self, input_x=-400, input_y=0, output_x=400, output_y=0):
        nodes = self.node_tree.nodes
        input = nodes.new("NodeGroupInput")
        input.location.x = input_x
        input.location.y = input_y
        output = nodes.new("NodeGroupOutput")
        output.location.x = output_x
        output.location.y = output_y
        self.input = input
        self.output = output
        return (input, output)

    def add_input_socket(self, name, socket_type="NodeSocketFloat", default_value=None):
        if not socket_type in _SOCKET_TYPES:
            raise ValueError("Illegal socket type")
        socket = self.node_tree.inputs.new(name=name, type=socket_type)
        if not default_value is None:
            socket.default_value=default_value
        return socket

    def add_output_socket(self, name, socket_type="NodeSocketFloat", default_value=None):
        if not socket_type in _SOCKET_TYPES:
            raise ValueError("Illegal socket type")
        socket = self.node_tree.outputs.new(name=name, type=socket_type)
        if not default_value is None:
            socket.default_value=default_value
        return socket

    def add_link(self, output_node, output_socket_name, input_node, input_socket_name):

        output_socket = None
        input_socket = None

        for socket in output_node.outputs:
            #print("OUTPUT " + output_socket_name + " " + socket.identifier)
            if socket.identifier == output_socket_name:
                output_socket = socket
                break

        if not output_socket:
            for socket in output_node.outputs:
                #print("OUTPUT " + output_socket_name + " " + socket.identifier)
                if socket.name == output_socket_name:
                    output_socket = socket
                    break

        for socket in input_node.inputs:
            #print("INPUT '" + str(input_socket_name) + "' '" + str(socket.identifier) + "'")
            if socket.identifier == input_socket_name:
                input_socket = socket
                break

        if not input_socket:
            for socket in input_node.inputs:
                #print("INPUT '" + str(input_socket_name) + "' '" + str(socket.identifier) + "'")
                if socket.name == input_socket_name:
                    input_socket = socket
                    break

        if not output_socket:
            raise ValueError("Output socket " + output_socket_name + " does not exist on " + str(output_node))
        if not input_socket:
            raise ValueError("Input socket " + input_socket_name + " does not exist on " + str(input_node))

        _LOG.debug("will create new link", (output_socket, input_socket))

        self.node_tree.links.new(output_socket, input_socket)
