from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("entities.nodemodel")
_LOG.trace("initializing nodemodel module")

_LOG.set_level(LogService.DUMP)
class InternalNodeManager:
    def __init__(self, node_tree):
        _LOG.trace("Constructing AtomNodeManager with node_tree", node_tree)
        self.node_tree = node_tree

    def _set_attribute(self, node, attribute_name, attribute_value):
        _LOG.debug("Starting attempt to set attribute", (attribute_name, attribute_value))
        if attribute_value is None:
            return
        if hasattr(node, attribute_name):
            setattr(node, attribute_name, attribute_value)
            _LOG.debug("Set attribute value", (node, attribute_name, attribute_value))
            _LOG.debug("Attribute value is now", (node, getattr(node, attribute_name)))
            return
        _LOG.warn("Failed to set attribute", (attribute_name, attribute_value))

    def _set_input_value(self, node, input_name, input_value):
        _LOG.debug("Starting attempt to set input value", (input_name, input_value))
        if input_value is None:
            return
        for socket in node.inputs:
            if socket.identifier == input_name or socket.name == input_name:
                socket.default_value = input_value
                _LOG.debug("Set input value", (input_name, input_value))
                return
        _LOG.warn("Failed to set input value", (input_name, input_value))

    def _set_output_value(self, node, output_name, output_value):
        _LOG.debug("Starting attempt to set output value", (output_name, output_value))
        if output_value is None:
            return
        for socket in node.outputs:
            if socket.identifier == output_name or socket.name == output_name:
                if hasattr(socket, "default_value"):
                    socket.default_value = output_value
                    _LOG.debug("Set output value", (output_name, output_value))
                    return
        _LOG.warn("Failed to set output value", (output_name, output_value))

    def _create_node(self, node_def):
        _LOG.debug("Create node", node_def)
        node = self.node_tree.nodes.new(node_def["class"])

        for attribute_name in node_def["attributes"].keys():
            self._set_attribute(node, str(attribute_name), node_def["attributes"][attribute_name])

        for attribute_name in ["name", "color", "label"]:
            if attribute_name in node_def:
                self._set_attribute(node, str(attribute_name), node_def[attribute_name])

        for input_name in node_def["inputs"].keys():
            self._set_input_value(node, str(input_name), node_def["inputs"][input_name])

        for output_name in node_def["outputs"].keys():
            self._set_output_value(node, str(output_name), node_def["outputs"][output_name])

        if "x" in node_def and node_def["x"]:
            node.location.x = node_def["x"]

        if "y" in node_def and node_def["y"]:
            node.location.y = node_def["y"]

        return node
