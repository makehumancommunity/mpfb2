import bpy, importlib
from mpfb.services.logservice import LogService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.primitives import *

_LOG = LogService.get_logger("nodemodel.v2.abstractgroupwrapper")
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

class AbstractGroupWrapper(AbstractNodeWrapper):
    def __init__(self, group_def, tree_def=None):
        _LOG.trace("Constructing group wrapper for", group_def["class"])
        AbstractNodeWrapper.__init__(self, group_def)
        self.tree_def = tree_def

    def validate_tree_against_original_def(self):
        if not self.tree_def:
            raise ValueError('No tree def registered for composite ' + self.node_class_name)
        node_tree = bpy.data.node_groups[self.node_class_name]
        if not node_tree:
            raise ValueError('Could not find node tree for ' + self.node_class_name)
        node_names_in_tree = []
        node_names_in_def = []

        for node in node_tree.nodes:
            node_names_in_tree.append(node.name)

        for node in self.tree_def["nodes"]:
            node_names_in_def.append(node["name"])

        missing_nodes = list(set(node_names_in_def) - set(node_names_in_tree))
        superfluous_nodes = list(set(node_names_in_tree) - set(node_names_in_def))

        if len(missing_nodes) < 1 and len(superfluous_nodes) < 1:
            return True

        for superfluous in superfluous_nodes:
            _LOG.warn("Superfluous node", (self.node_class_name, superfluous))

        for missing in missing_nodes:
            _LOG.error("Node is missing", (self.node_class_name, missing))

        return False

    @staticmethod
    def get_wrapper(node_class_name):
        _LOG.enter()
        wrapper = None
        if node_class_name in PRIMITIVE_NODE_WRAPPERS:
            wrapper = PRIMITIVE_NODE_WRAPPERS[node_class_name]
        else:
            try:
                mod = importlib.import_module(".nodewrapper" + node_class_name.lower(), package="mpfb.entities.nodemodel.v2.composites")
                if mod and hasattr(mod, "NodeWrapper" + node_class_name):
                    wrapper = getattr(mod, "NodeWrapper" + node_class_name)
            except Exception as e:
                _LOG.error("Import error for ", (node_class_name, e))
        return wrapper

    @staticmethod
    def node(node_class_name, node_tree, name=None, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
        _LOG.enter()
        wrapper = AbstractGroupWrapper.get_wrapper(node_class_name)
        if not wrapper:
            _LOG.error('No such node or group: ' + node_class_name)
            raise ValueError('No such node or group: ' + node_class_name)
        inst = wrapper.create_instance(node_tree, name=name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)
        _LOG.debug("Created node", inst)
        return inst

    @staticmethod
    def add_input_socket(node_tree, name, socket_type="NodeSocketFloat", default_value=None):
        _LOG.enter()
        if not socket_type in _SOCKET_TYPES:
            raise ValueError("Illegal socket type " + socket_type)
        socket = node_tree.inputs.new(name=name, type=socket_type)
        if not default_value is None:
            socket.default_value=default_value
        _LOG.debug("Created input socket", socket)
        return socket

    @staticmethod
    def add_output_socket(node_tree, name, socket_type="NodeSocketFloat", default_value=None):
        _LOG.enter()
        if not socket_type in _SOCKET_TYPES:
            raise ValueError("Illegal socket type " + socket_type)
        socket = node_tree.outputs.new(name=name, type=socket_type)
        if not default_value is None:
            socket.default_value=default_value
        _LOG.debug("Created output socket", socket)
        return socket

    @staticmethod
    def create_link(node_tree, from_node, from_socket, to_node, to_socket):
        _LOG.enter()
        fsocket = None
        tsocket = None
        _LOG.debug("create link", (from_node, from_socket, to_node, to_socket))
        for socket in from_node.outputs:
            if socket.identifier == from_socket:
                fsocket = socket
        if not fsocket:
            for socket in from_node.outputs:
                if socket.name == from_socket:
                    fsocket = socket
        if not fsocket:
            _LOG.error("Could not find output socket '" + from_socket + "' on node '" + from_node.name + "'")
            raise ValueError("Could not find output socket '" + from_socket + "' on node '" + from_node.name + "'")

        for socket in to_node.inputs:
            if socket.identifier == to_socket:
                tsocket = socket
        if not tsocket:
            for socket in to_node.inputs:
                if socket.name == to_socket:
                    tsocket = socket
        if not tsocket:
            _LOG.error("Could not find input socket '" + to_socket + "' on node '" + to_node.name + "'")
            raise ValueError("Could not find input socket '" + to_socket + "' on node '" + to_node.name + "'")

        link = node_tree.links.new(fsocket, tsocket)
        _LOG.debug("Created new link", link)
        return link

    def create_node_tree(self):
        _LOG.enter()
        node_tree = NodeService.create_node_tree(self.node_class_name)

        input = NodeService.find_first_node_by_type_name(node_tree, "NodeGroupInput")
        if not input:
            input = node_tree.nodes.new("NodeGroupInput")

        output = NodeService.find_first_node_by_type_name(node_tree, "NodeGroupOutput")
        if not output:
            output = node_tree.nodes.new("NodeGroupOutput")

        for input_name in self.node_def["inputs"]:
            input_def = self.node_def["inputs"][input_name]
            socket = AbstractGroupWrapper.add_input_socket(node_tree, input_def["name"], input_def["class"], input_def["default_value"])
        for output_name in self.node_def["outputs"]:
            output_def = self.node_def["outputs"][output_name]
            socket = AbstractGroupWrapper.add_output_socket(node_tree, output_def["name"], output_def["class"], output_def["default_value"])

        return node_tree

    def pre_create_instance(self, node_tree):
        _LOG.enter()
        if not self.node_class_name in bpy.data.node_groups:
            group_tree = self.create_node_tree()
            nodes = dict()
            nodes["Group Input"] = NodeService.find_first_node_by_type_name(group_tree, "NodeGroupInput")
            nodes["Group Input"].name = "Group Input"
            nodes["Group Input"].label = ""
            nodes["Group Input"].use_custom_color = True
            nodes["Group Input"].color = [0.0, 0.35, 0.35]
            nodes["Group Output"] = NodeService.find_first_node_by_type_name(group_tree, "NodeGroupOutput")
            nodes["Group Output"].name = "Group Output"
            nodes["Group Output"].label = ""
            nodes["Group Output"].use_custom_color = True
            nodes["Group Output"].color = [0.0, 0.35, 0.35]
            self.setup_group_nodes(group_tree, nodes)

    def setup_group_nodes(self, node_tree, nodes):
        _LOG.enter()
        raise NotImplementedError(self.node_class_name + " did not override the setup_group_nodes() method")