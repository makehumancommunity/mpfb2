import bpy, os
from mpfb.services.logservice import LogService
from mpfb.services.nodeservice import NodeService
from mpfb.services.systemservice import SystemService
from mathutils import Euler

_LOG = LogService.get_logger("nodemodel.v2.abstractnodewrapper")

_VALID_ARRAY_TYPES = ["tuple", "list", "array", "Vector", "Color", "NodeSocketColor", "NodeSocketVector", "NodeSocketRotation"]
_VALID_NUMERIC_TYPES = ["int", "float", "NodeSocketFloat", "NodeSocketFloatFactor", "NodeSocketInt", "NodeSocketIntFactor", "NodeSocketFloatDistance"]
_VALID_STRING_TYPES = ["str", "enum"]

class AbstractNodeWrapper():

    def __init__(self, node_def):
        self.node_def = node_def
        self.node_class_name = self.node_def["class"]

    def _validate_names(self, input_socket_values=None, attribute_values=None, output_socket_values=None):
        if input_socket_values:
            for key in input_socket_values:
                isvalid = False
                for input in self.node_def["inputs"].keys():
                    ndef = self.node_def["inputs"][input]
                    if key == str(input) or key == ndef["name"] or key == ndef["identifier"]:
                        isvalid = True
                if not isvalid:
                    _LOG.error(key + " is not a valid input socket for " + self.node_class_name)
                    raise ValueError(key + " is not a valid input socket for " + self.node_class_name)
        if output_socket_values:
            for key in output_socket_values:
                if not key in self.node_def["outputs"]:
                    _LOG.error(key + " is not a valid output socket for " + self.node_class_name)
                    raise ValueError(key + " is not a valid output socket for " + self.node_class_name)
        if attribute_values:
            for key in attribute_values:
                if not key in self.node_def["attributes"]:
                    _LOG.error(key + " is not a valid attribute for " + self.node_class_name)
                    raise ValueError(key + " is not a valid attribute for " + self.node_class_name)

    def _check_is_valid_assignment(self, value, definition_class):
        value_class = type(value).__name__
        if value_class == definition_class:
            return True
        if value_class in _VALID_NUMERIC_TYPES and definition_class in _VALID_NUMERIC_TYPES:
            return True
        if value_class in _VALID_ARRAY_TYPES and definition_class in _VALID_ARRAY_TYPES:
            return True
        if value_class in _VALID_STRING_TYPES and definition_class in _VALID_STRING_TYPES:
            return True
        return False

    def _set_attributes(self, node, attribute_values, forgiving=False):
        if not attribute_values:
            return
        for key in attribute_values:
            value = attribute_values[key]
            attribute = self.node_def["attributes"][key]
            if attribute["class"] == "image":
                if value and value["filepath"]:
                    image_path_absolute = value["filepath"]
                    image_file_name = os.path.basename(value["filepath"])
                    if image_file_name in bpy.data.images:
                        _LOG.debug("image was previously loaded", image_path_absolute)
                        image = bpy.data.images[image_file_name]
                    else:
                        _LOG.debug("image needs loading", image_path_absolute)
                        image = bpy.data.images.load(image_path_absolute)
                    colorspace = value["colorspace"]
                    if colorspace:
                        try:
                            image.colorspace_settings.name = colorspace
                        except:
                            _LOG.debug("could not assign colorspace", (image_file_name, colorspace))
                    node.image = image
            else:
                if not self._check_is_valid_assignment(value, attribute["class"]):
                    _LOG.error("Cannot use '" + str(value) + "' as value for " + key + " attribute of " + self.node_class_name + ". Expected value of type " + attribute["class"] + ".")
                    raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " attribute of " + self.node_class_name + ". Expected value of type " + attribute["class"] + ".")
                setattr(node, key, value)

    def _set_input_sockets(self, node, input_socket_values, forgiving=False):
        if not input_socket_values:
            return
        for key in input_socket_values:
            value = input_socket_values[key]
            input = None
            if key in self.node_def["inputs"]:
                input = self.node_def["inputs"][key]
            else:
                for namekey in self.node_def["inputs"].keys():
                    ndef = self.node_def["inputs"][namekey]
                    if key == ndef["name"] or key == ndef["identifier"]:
                        input = ndef
            if not self._check_is_valid_assignment(value, input["class"]):
                _LOG.error("Cannot use '" + str(value) + "' as value for " + key + " input of " + self.node_class_name + ". Expected value of type " + input["class"] + ".")
                raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " input of " + self.node_class_name + ". Expected value of type " + input["class"] + ".")
            input_socket = NodeService.find_input_socket_by_identifier_or_name(node, key, key)
            if not input_socket:
                _LOG.error("Input socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)
                if str(node.__class__.__name__) == "ShaderNodeGroup":
                    _LOG.error("Target is a group", node.node_tree.name)
                _LOG.error("Input socket values", input_socket_values)
                _LOG.error("Node", node)
                raise KeyError("Input socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)
            input_socket.default_value = value

    def _set_output_sockets(self, node, output_socket_values, forgiving=False):
        if not output_socket_values:
            return
        for key in output_socket_values:
            value = output_socket_values[key]
            output = self.node_def["outputs"][key]
            if not self._check_is_valid_assignment(value, output["class"]):
                _LOG.error("Cannot use '" + str(value) + "' as value for " + key + " output of " + self.node_class_name + ". Expected value of type " + output["class"] + ".")
                raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " output of " + self.node_class_name + ". Expected value of type " + output["class"] + ".")
            output_socket = NodeService.find_output_socket_by_identifier_or_name(node, key, key)
            if not output_socket:
                _LOG.error("Output socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)
                raise KeyError("Output socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)
            if hasattr(output_socket, "default_value"):
                output_socket.default_value = value
            else:
                _LOG.warn("Output socket did not have default_value attribute", output_socket)

    def _is_same(self, value_class, node_value, default_value):
        if default_value is None:
            return False
        try:
            if isinstance(node_value, Euler):
                node_value = [node_value.x, node_value.y, node_value.z]
            if node_value is None:
                return True
            if value_class in _VALID_ARRAY_TYPES:
                for i in range(len(node_value)):
                    delta = node_value[i] - default_value[i]
                    if abs(delta) > 0.00009:
                        return False
                return True
            if value_class in _VALID_NUMERIC_TYPES:
                delta = node_value - default_value
                return abs(delta) < 0.00009
            return node_value == default_value
        except TypeError as e:
            _LOG.error("Cannot compare", {
                "value_class": value_class,
                "node_value": node_value,
                "default_value": default_value,
                "node_value_type": type(node_value).__name__
                })
            raise e

    def _cleanup(self, value):
        if type(value).__name__ in ["Vector", "Color"]:
            return list(value)
        if type(value).__name__ == "Euler":
            return [value.x, value.y, value.z]
        return value

    def find_non_default_settings(self, node):
        nc = node.__class__.__name__
        isgroup = nc == "ShaderNodeGroup"
        if nc != self.node_class_name and nc != "ShaderNodeGroup":
            raise ValueError("Cannot compare " + node.__class__.__name__ + " with " + self.node_class_name)

        comparison = dict()
        comparison["attribute_values"] = dict()
        comparison["input_socket_values"] = dict()
        comparison["output_socket_values"] = dict()

        _LOG.debug("Starting attribute detection for", (node, self.node_class_name))

        for key in self.node_def["attributes"]:

            attribute = self.node_def["attributes"][key]
            default_value = attribute["value"]
            node_value = getattr(node, attribute["name"])
            value_class = attribute["class"]

            _LOG.trace("Found attribute", (key, node_value))

            if value_class == "image":
                fp = NodeService.get_image_file_path(node)
                if not default_value or fp != default_value["filepath"]:
                    comparison["attribute_values"][key] = dict()
                    comparison["attribute_values"][key]["filepath"] = fp
                    comparison["attribute_values"][key]["colorspace"] = node.image.colorspace_settings.name
            else:
                if nc == "ShaderNodeGroup" or not self._is_same(value_class, node_value, default_value):
                    if node_value is not None:
                        comparison["attribute_values"][key] = self._cleanup(node_value)

        _LOG.debug("Attributes", comparison["attribute_values"])

        for key in self.node_def["inputs"]:
            socket_def = self.node_def["inputs"][key]
            default_value = socket_def["default_value"]
            _LOG.debug("Socket def", socket_def)
            socket = NodeService.find_input_socket_by_identifier_or_name(node, socket_def["identifier"], socket_def["name"])
            _LOG.debug("Socket", socket)
            node_value = None
            if hasattr(socket, "default_value"):
                socket_type = socket_def["value_type"]
                if socket_type in ["RGB", "RGBA", "VECTOR"]:
                    node_value = list(socket.default_value)
                else:
                    node_value = socket.default_value
            value_class = socket_def["class"]
            skip = False
            if SystemService.is_blender_version_at_least([4,0,0]) and socket_def["name"] == "Sheen Tint":
                # Socket has changed type from float to color in blender 4. Until we know that this is
                # intended and final, we'll just skip this particular socket.
                # TODO: Revisit this when b4 is stable
                skip = True
            if not skip:
                if not self._is_same(value_class, node_value, default_value):
                    if isgroup:
                        comparison["input_socket_values"][socket_def["name"]] = self._cleanup(node_value)
                    else:
                        comparison["input_socket_values"][key] = self._cleanup(node_value)

        for key in self.node_def["outputs"]:
            socket_def = self.node_def["outputs"][key]
            default_value = socket_def["default_value"]
            socket = NodeService.find_output_socket_by_identifier_or_name(node, socket_def["identifier"], socket_def["name"])
            node_value = None
            if hasattr(socket, "default_value"):
                node_value = socket.default_value
            value_class = socket_def["class"]
            if not self._is_same(value_class, node_value, default_value):
                if key != "BSDF":
                    comparison["output_socket_values"][key] = self._cleanup(node_value)

        return comparison

    def create_instance(self, node_tree, name=None, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
        from . import PRIMITIVE_NODE_WRAPPERS
        self.pre_create_instance(node_tree)
        self._validate_names(input_socket_values, attribute_values, output_socket_values)
        if self.node_class_name in PRIMITIVE_NODE_WRAPPERS:
            node = node_tree.nodes.new(self.node_class_name)
            if node.__class__.__name__ != self.node_class_name:
                _LOG.error("Created node ended up having the wrong type", (self.node_class_name, node.__class__.__name__))
                raise ValueError("Could not create instance of " + self.node_class_name)
        else:
            # Assuming we're going to create a group
            node = node_tree.nodes.new("ShaderNodeGroup")
            node.node_tree = bpy.data.node_groups[self.node_class_name]
        self._set_attributes(node, attribute_values)
        self._set_input_sockets(node, input_socket_values)
        self._set_output_sockets(node, output_socket_values)
        if name:
            node.name = name
        if label:
            node.label = label
        else:
            if name:
                node.label = name
        return node

    def pre_create_instance(self, node_tree):
        pass
