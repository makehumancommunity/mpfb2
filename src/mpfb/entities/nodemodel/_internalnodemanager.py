from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("entities.nodemodel")
_LOG.trace("initializing nodemodel module")

class InternalNodeManager:
    def __init__(self, node_tree):
        _LOG.trace("Constructing AtomNodeManager with node_tree", node_tree)
        self.node_tree = node_tree

    def _create_node(self, node_def):
        _LOG.debug("Create node", node_def)
        node = self.node_tree.nodes.new(node_def["class"])
        return node
