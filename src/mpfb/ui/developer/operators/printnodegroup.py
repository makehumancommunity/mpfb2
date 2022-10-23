"""Functionality for printing a node group to the console"""

from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES
import bpy
from string import Template

_LOG = LogService.get_logger("developer.operators.printnodegroup")
_LOG.set_level(LogService.DEBUG)

_TEST_ATTRIBUTES=[
    "air_density",
    "altitude",
    "attribute_name",
    "attribute_type",
    "axis",
    "bands_direction",
    "blend_type",
    "bytecode",
    "bytecode_hash",
    "cache_point_density",
    "calc_point_density",
    "calc_point_density_minmax",
    "clamp",
    "clamp_type",
    "color_mapping",
    "color_ramp",
    "component",
    "convert_from",
    "convert_to",
    "data_type",
    "direction_type",
    "distance",
    "distribution",
    "dust_density",
    "extension",
    "falloff",
    "feature",
    "filepath",
    "from_instancer",
    "gradient_type",
    "ground_albedo",
    "ies",
    "image",
    "image_user",
    "inside",
    "interface",
    "interpolation",
    "interpolation_type",
    "invert",
    "is_active_output",
    "layer_name",
    "mapping",
    "mode",
    "musgrave_dimensions",
    "musgrave_type",
    "node_tree",
    "noise_dimensions",
    "object",
    "offset",
    "offset_frequency",
    "only_local",
    "operation",
    "ozone_density",
    "parametrization",
    "particle_color_source",
    "particle_system",
    "point_source",
    "projection",
    "projection_blend",
    "radius",
    "resolution",
    "rings_direction",
    "rotation_type",
    "samples",
    "script",
    "sky_type",
    "space",
    "squash",
    "squash_frequency",
    "subsurface_method",
    "sun_direction",
    "sun_disc",
    "sun_elevation",
    "sun_intensity",
    "sun_rotation",
    "sun_size",
    "target",
    "texture_mapping",
    "turbidity",
    "turbulence_depth",
    "use_alpha",
    "use_auto_update",
    "use_clamp",
    "use_pixel_size",
    "use_tips",
    "uv_map",
    "wave_profile",
    "wave_type",
    "vector_type",
    "vertex_attribute_name",
    "vertex_color_source",
    "voronoi_dimensions"
    ]

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

        types_with_output_default_values = [
            "ShaderNodeValue"
            ]

        group = None
        selected = context.selected_nodes
        scene = context.scene

        output_name = DEVELOPER_PROPERTIES.get_value("output_class_name", entity_reference=scene)

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

        output_lower = str(output_name).lower().replace("mpfb", "")
        print(Template("""
from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.${output_lower}")
_GROUP_NAME = "${output_name}"

class ${output_name}(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)""").substitute(output_name=output_name, output_lower=output_lower))
        print("")
        ind = "        "
        print(ind + "nodes = dict()\n")
        print(ind + "(nodes[\"Group Input\"], nodes[\"Group Output\"]) = self.create_input_and_output()")
        for node in node_tree.nodes:
            if node.__class__.__name__ == "NodeGroupInput":
                print(ind + "nodes[\"Group Input\"].location = [" + str(node.location.x) + ", " + str(node.location.y) + "]")
            if node.__class__.__name__ == "NodeGroupOutput":
                print(ind + "nodes[\"Group Output\"].location = [" + str(node.location.x) + ", " + str(node.location.y) + "]")

        print("")

        for input in group.inputs:
            name = input.name
            socket_type = input.__class__.__name__
            if socket_type != "NodeSocketVirtual":
                line = ind + "self.add_input_socket(\"" + name + "\", socket_type=\"" + socket_type + "\""
                if hasattr(input, "default_value"):
                    value = str(input.default_value)
                    if type(input.default_value).__name__ == "bpy_prop_array":
                        value = str(list(input.default_value))
                    line = line + ", default_value=" + value
                line = line + ")"
                print(line)

        print("")

        for input in group.outputs:
            name = input.name
            socket_type = input.__class__.__name__
            if socket_type != "NodeSocketVirtual":
                line = ind + "self.add_output_socket(\"" + name + "\", socket_type=\"" + socket_type + "\""
                if hasattr(input, "default_value"):
                    value = str(input.default_value)
                    if type(input.default_value).__name__ == "bpy_prop_array":
                        value = str(list(input.default_value))
                    line = line + ", default_value=" + value
                print(line + ")")

        print("")

        for node in node_tree.nodes:
            if node.__class__.__name__ not in ["NodeGroupOutput", "NodeGroupInput"]:
                line = ind + "nodes[\"" + node.name + "\"] = self.create" + node.__class__.__name__ + "("
                line = line + "name=\"" + node.name + "\""
                if (node.label):
                    line = line + ", label=\"" + node.label + "\""
                line = line + ", x=" + str(node.location.x)
                line = line + ", y=" + str(node.location.y)

                for input in node.inputs:
                    if not hasattr(input, "identifier"):
                        name = str(input.name).replace(" ", "_")
                    else:
                        name = str(input.identifier).replace(" ", "_")
                    socket_type = input.__class__.__name__
                    value = None
                    if socket_type != "NodeSocketVirtual":
                        if hasattr(input, "default_value"):
                            value = str(input.default_value)
                            if type(input.default_value).__name__ == "bpy_prop_array":
                                value = str(list(input.default_value))

                    if not value is None:
                        line = line + ", " + name + "=" + str(value)

                if node.__class__.__name__ in types_with_output_default_values:
                    for input in node.outputs:
                        if not hasattr(input, "identifier"):
                            name = str(input.name).replace(" ", "_")
                        else:
                            name = str(input.identifier).replace(" ", "_")
                        socket_type = input.__class__.__name__
                        value = None
                        if socket_type != "NodeSocketVirtual":
                            if hasattr(input, "default_value"):
                                value = str(input.default_value)
                                if type(input.default_value).__name__ == "bpy_prop_array":
                                    value = str(list(input.default_value))

                        if not value is None:
                            line = line + ", " + name + "=" + str(value)

                for attribute_name in _TEST_ATTRIBUTES:
                    if hasattr(node, attribute_name):
                        value = getattr(node, attribute_name)
                        if type(value) is str:
                            value = "'" + value + "'"
                        if not value is None:
                            line = line + ", " + str(attribute_name).replace(" ", "_") + "=" + str(value)

                line = line + ")"
                print(line)

        print("")

        for link in node_tree.links:
            from_node = link.from_node
            from_socket = link.from_socket
            to_node = link.to_node
            to_socket = link.to_socket

            from_name = from_socket.name
            if hasattr(from_socket, "identifier") and not from_node.name == "Group Input":
                from_name = from_socket.identifier

            to_name = to_socket.name
            if hasattr(to_socket, "identifier") and not to_node.name == "Group Output":
                to_name = to_socket.identifier

            line = ind + "self.add_link(nodes[\"" + from_node.name + "\"], \"" + from_name + "\", "
            line = line + "nodes[\"" + to_node.name + "\"], \"" + to_name + "\")"
            print(line)

        print("\n\n")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Print_Node_Group_Operator)
