import bpy

_VALID_ARRAY_TYPES = ["tuple", "list", "array", "Vector", "Color", "NodeSocketColor", "NodeSocketVector"]
_VALID_NUMERIC_TYPES = ["int", "float", "NodeSocketFloat", "NodeSocketFloatFactor", "NodeSocketInt", "NodeSocketIntFactor"]
_VALID_STRING_TYPES = ["str", "enum"]

class AbstractNodeWrapper():
    
    def __init__(self, node_def):
        self.node_def = node_def
        self.node_class_name = self.node_def["class"]            
    
    def _validate_names(self, input_socket_values=None, attribute_values=None, output_socket_values=None):
        if input_socket_values:
            for key in input_socket_values:
                if not key in self.node_def["inputs"]:
                    raise ValueError(key + " is not a valid input socket for " + self.node_class_name)
        if output_socket_values:
            for key in output_socket_values:
                if not key in self.node_def["outputs"]:
                    raise ValueError(key + " is not a valid output socket for " + self.node_class_name)
        if attribute_values:
            for key in attribute_values:
                if not key in self.node_def["attributes"]:
                    raise ValueError(key + " is not a valid attribute for " + self.node_class_name)                
    
    def _find_socket(self, socket_list, socket_id):
        for socket in socket_list:
            if socket.identifier == socket_id:
                return socket
        for socket in socket_list:
            if socket.name == socket_id:
                return socket
        return None
    
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
        
    def _set_attributes(self, node, attribute_values):
        if not attribute_values:
            return
        for key in attribute_values:
            value = attribute_values[key]
            attribute = self.node_def["attributes"][key]                                    
            if not self._check_is_valid_assignment(value, attribute["class"]):
                raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " attribute of " + self.node_class_name + ". Expected value of type " + attribute["class"] + ".")
            setattr(node, key, value)

    def _set_input_sockets(self, node, input_socket_values):
        if not input_socket_values:
            return
        for key in input_socket_values:
            value = input_socket_values[key]
            input = self.node_def["inputs"][key]                                    
            if not self._check_is_valid_assignment(value, input["class"]):
                raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " input of " + self.node_class_name + ". Expected value of type " + input["class"] + ".")
            input_socket = self._find_socket(node.inputs, key)
            if not input_socket:
                raise KeyError("Input socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)            
            input_socket.default_value = value

    def _set_output_sockets(self, node, output_socket_values):
        if not output_socket_values:
            return
        for key in output_socket_values:
            value = output_socket_values[key]
            output = self.node_def["outputs"][key]                                    
            if not self._check_is_valid_assignment(value, output["class"]):
                raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " output of " + self.node_class_name + ". Expected value of type " + output["class"] + ".")
            output_socket = self._find_socket(node.outputs, key)
            if not output_socket:
                raise KeyError("Output socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)            
            output_socket.default_value = value
                        
    def create_instance(self, node_tree, name=None, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None, forgiving=False):
        self._validate_names(input_socket_values, attribute_values, output_socket_values)        
        node = node_tree.nodes.new(self.node_class_name)
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
    
    
    