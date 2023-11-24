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
        if not mhmat or not node or not mhmat_key:
            return
        file_name = mhmat.get_value(mhmat_key)
        _LOG.debug("Assigning material image", (node, node.__class__.__name__, mhmat_key, file_name))
        if "image" not in str(node.__class__.__name__).lower():
            _LOG.debug("Not an image node", (node, node.__class__.__name__))
            return
        if not file_name or not str(file_name).strip():
            _LOG.debug("No file set for mhmat key", mhmat_key)
            return
        _LOG.debug("About to assign material image", (mhmat_key, file_name))
        colorspace = "sRGB"
        if "normal" in mhmat_key:
            colorspace = "Non-Color"
        NodeService.set_image_in_image_node(node, file_name, colorspace=colorspace)

    def ensure_exists(self):
        pass

    def create_instance(self, node_tree, name=None, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None, mhmat=None):
        if mhmat:
            self.pre_create_instance(node_tree, mhmat=mhmat)
        else:
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
        if mhmat:
            self.setup_group_nodes(node_tree, nodes, mhmat=mhmat)
        else:
            self.setup_group_nodes(node_tree, nodes)