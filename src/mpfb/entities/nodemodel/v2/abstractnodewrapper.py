import bpy

class AbstractNodeWrapper():
    
    def __init__(self, node_class_name):
        self.node_class_name = node_class_name
        
    def create_instance(self, node_tree, name=None, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
        node = node_tree.nodes.new(self.node_class_name)
        if name:
            node.name = name
        if label:
            node.label = label
        else:
            if name:
                node.label = name
        return node
    
    
    