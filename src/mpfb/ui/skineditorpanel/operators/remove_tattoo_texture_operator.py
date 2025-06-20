from mpfb.services.logservice import LogService
from mpfb.services.skineditorservices import SkinEditorService
from mpfb.services.locationservice import LocationService
from mpfb._classmanager import ClassManager
import bpy, os, json, shutil

_LOG = LogService.get_logger("skineditorpanel.remove_tattoo_texture_operator")


class MPFB_OT_RemoveTattooTexture_Operator(bpy.types.Operator):
    """Removes tattoo"""

    bl_idname = "mpfb.remove_tattoo_texture_operator"
    bl_label = "remove tattoo"
    bl_options = {'REGISTER'}

    tattoo_name: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        tattoo_path = scene.tattoo_texture_path
        self.report({'INFO'}, ("Removing tattoo file, it might take a while..."))

        material = context.object.active_material

        if not material or not material.node_tree:
            self.report({'ERROR'}, "No active material found!")
            return {'CANCELLED'}

        node_tree = material.node_tree
        nodes = node_tree.nodes

        texture_node_label = "mapped" + self.tattoo_name
        texture_node = None

        # Find texture node
        for node in nodes:
            if node.label == texture_node_label:
                texture_node = node
                break

        if not texture_node:
            self.report({'ERROR'}, f"Texture node '{texture_node_label}' not found!")
            return {'CANCELLED'}

        # Find node connected to Color output of the texture
        color_links = texture_node.outputs.get("Color").links
        node1 = color_links[0].to_node if color_links else None

        # Find node connected to Alpha output of the texture
        alpha_links = texture_node.outputs.get("Alpha").links
        node2 = alpha_links[0].to_node if alpha_links else None

        if node2:
            # Find node3 that goes into Color1 of node2
            node3 = None
            if "Color1" in node2.inputs and node2.inputs["Color1"].links:
                node3 = node2.inputs["Color1"].links[0].from_node

            # Find node4 that receives color output from node2
            node4 = None
            if node2.outputs.get("Color") and node2.outputs["Color"].links:
                node4_input = node2.outputs["Color"].links[0].to_socket
                node4 = node2.outputs["Color"].links[0].to_node

            # Reconnect node3 color output to node4 input
            if node3 and node4 and node4_input:
                node_tree.links.new(node3.outputs.get("Color"), node4_input)

            # Remove node2
            nodes.remove(node2)

        # Remove node1
        if node1:
            nodes.remove(node1)

        # Remove texture node
        nodes.remove(texture_node)

        # Remove the tattoo influence property
        influence_property = "tattoo_influence_" + self.tattoo_name

        if hasattr(bpy.types.Scene, influence_property):
            delattr(bpy.types.Scene, influence_property)

        # refresh ui
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        self.report({'INFO'}, f"Successfully removed tattoo '{self.tattoo_name}'")


        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_RemoveTattooTexture_Operator)