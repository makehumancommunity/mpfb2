import bpy, importlib
from mpfb.services.logservice import LogService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.primitives import *
from mpfb.entities.nodemodel.v2.composites import *

_LOG = LogService.get_logger("nodemodel.v2.abstractmaterialwrapper")

class AbstractMaterialWrapper(AbstractGroupWrapper):

    def __init__(self, fake_node_class_name, tree_def):
        _LOG.trace("Constructing material wrapper for " + fake_node_class_name)
        node_def = dict()
        node_def["class"] = fake_node_class_name
        AbstractNodeWrapper.__init__(self, node_def)
        self.tree_def = tree_def

    def assign_mhmat_image(self, node, mhmat_key, mhmat):
        if not mhmat:
            return

    def ensure_exists(self):
        pass

    def create_instance(self, node_tree, name=None, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None, mhmat=None):
        self.pre_create_instance(node_tree)
        return None

    def pre_create_instance(self, node_tree=None, mhmat=None):
        _LOG.enter()
        if not node_tree:
            raise ValueError('Must pass an existing node tree for material creation')
        nodes = dict()
        _LOG.debug("Node tree", node_tree)
        for node in node_tree.nodes:
            _LOG.debug("Node", node)
            if node.name == "Material Output":
                nodes["Material Output"] = node
            else:
                node_tree.nodes.remove(node)
        if not "Material Output" in nodes:
            nodes["Material Output"] = node_tree.nodes.new("ShaderNodeOutputMaterial")
            nodes["Material Output"].name = "Material Output"
        self.setup_group_nodes(node_tree, nodes)