"""Functionality for printing a node group to the console"""

from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("developer.operators.printnodegroup")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_Print_Node_Group_Operator(bpy.types.Operator):
    """Print the code representing a selected node group to the console """
    bl_idname = "mpfb.print_node_group"
    bl_label = "Print group code"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        area = str(context.area.ui_type)
        if area != "ShaderNodeTree":
            _LOG.trace("Wrong context ", area)
            return False

        selected = context.selected_nodes
        if not selected or len(selected) < 1:
            _LOG.trace("Nothing selected")
            return False

        for node in selected:
            classname = node.__class__.__name__
            _LOG.trace("Selected node class", classname)
            if classname == "ShaderNodeGroup":
                return True

        return False

    def execute(self, context):
        _LOG.enter()

        group = None
        selected = context.selected_nodes

        if len(selected) > 1:
            self.report({'ERROR'}, "More than one node selected")
            return {'FINISHED'}

        for node in selected:
            classname = node.__class__.__name__
            _LOG.debug("Selected node class", classname)
            if classname == "ShaderNodeGroup":
                group = node

        if not group:
            self.report({'ERROR'}, "No group node selected")
            return {'FINISHED'}

        node_tree = group.node_tree

        _LOG.debug("Group", group)

        print("\n\n")
        print("(input, output) = self.create_input_and_output()")
        for node in node_tree.nodes:
            if node.__class__.__name__ == "NodeGroupInput":
                for input in node.outputs:
                    name = input.name
                    socket_type = input.__class__.__name__
                    if socket_type != "NodeSocketVirtual":
                        line = "self.add_input_socket(\"" + name + "\", socket_type=\"" + socket_type + "\""
                        if hasattr(input, "default_value"):
                            value = str(input.default_value)
                            if type(input.default_value).__name__ == "bpy_prop_array":
                                value = str(list(input.default_value))
                            line = line + ", default_value=" + value
                        line = line + ")"
                        print(line)
        print("")

        for node in node_tree.nodes:
            if node.__class__.__name__ == "NodeGroupOutput":
                for input in node.inputs:
                    name = input.name
                    socket_type = input.__class__.__name__
                    if socket_type != "NodeSocketVirtual":
                        line = "self.add_output_socket(\"" + name + "\", socket_type=\"" + socket_type + "\""
                        if hasattr(input, "default_value"):
                            value = str(input.default_value)
                            if type(input.default_value).__name__ == "bpy_prop_array":
                                value = str(list(input.default_value))
                            line = line + ", default_value=" + value
                        line = line + ")"
                        print(line)

        print("")
        print("nodes = dict()\n")

        for node in node_tree.nodes:
            if node.__class__.__name__ not in ["NodeGroupOutput", "NodeGroupInput"]:
                line = "nodes[\"" + node.name + "\"] = self.create" + node.__class__.__name__ + "("
                line = line + "name=\"" + node.name + "\""
                if (node.label):
                    line = line + ", label=\"" + node.label + "\""
                line = line + ", x=" + str(node.location.x)
                line = line + ", y=" + str(node.location.y)

                for input in node.inputs:
                    name = str(input.name).replace(" ", "_")
                    socket_type = input.__class__.__name__
                    value = None
                    if socket_type != "NodeSocketVirtual":
                        if hasattr(input, "default_value"):
                            value = str(input.default_value)
                            if type(input.default_value).__name__ == "bpy_prop_array":
                                value = str(list(input.default_value))

                    if not value is None:
                        line = line + ", " + name + "=" + str(value)
                line = line + ")"
                print(line)

        print("")

        for link in node_tree.links:
            from_node = link.from_node
            from_socket = link.from_socket
            to_node = link.to_node
            to_socket = link.to_socket

            line = "self.add_link(nodes[\"" + from_node.name + "\"], \"" + from_socket.name + "\", "
            line = line + "nodes[\"" + to_node.name + "\"], \"" + to_socket.name + "\")"
            print(line)

        print("\n\n")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Print_Node_Group_Operator)
