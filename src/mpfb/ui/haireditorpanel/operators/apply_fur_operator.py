# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for loading fur assets, adding them to Human mesh and setting up UI for editing
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.locationservice import LocationService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
import bpy, os, json, shutil

_LOG = LogService.get_logger("haireditorpanel.apply_fur_operator")


class MPFB_OT_ApplyFur_Operator(bpy.types.Operator):
    """Adds fur asset"""
    bl_idname = "mpfb.apply_fur_operator"
    bl_label = "Apply fur"
    bl_options = {'REGISTER'}
    hair_asset: bpy.props.StringProperty()

    # Callback for editing geo-node modifiers based on hair shape properties
    def make_update_callback(self, hair_obj ,modifier_name, attribute_name, property_name, value_range=None):
        def callback(self, context):
            mod = hair_obj.modifiers.get(modifier_name)
            if mod:
                value = getattr(self, f"{hair_obj.name}_{property_name}")
                hair_obj.modifiers[modifier_name][attribute_name]=value
                hair_obj.update_tag()
                bpy.context.view_layer.update()
                hair_obj.hide_viewport = True
                hair_obj.hide_viewport = False
                if hasattr(mod, "node_group") and mod.node_group:
                    mod.node_group.interface_update(bpy.context)
        return callback

    # Callback for fur asset material
    def make_material_callback(self, material_name, attribute_name, input_name, prop_id):
        def callback(self, context):
            mat = bpy.data.materials.get(material_name)
            if not mat or not mat.use_nodes:
                print("Material not found")
                return

            for node in mat.node_tree.nodes:
                if node.name == 'Group':
                    material_node = node
                    break

            # Update the input value
            target_input = next((inp for inp in material_node.inputs if inp.name == input_name), None)
            if not target_input:
                print(f"Input '{input_name}' not found in node '{material_node.name}'")
                return

            val = getattr(self, f"{prop_id}")
            if hasattr(target_input, 'default_value'):
                target_input.default_value = val
        return callback

    # Callback for loading fur asset texture
    def make_texture_callback(self, material_name, prop_id):
        def callback(self, context):
            # Get the texture file path
            path = getattr(self, prop_id)
            if not path or not os.path.isfile(path):
                print(f"Texture path invalid: {path}")
                return

            # Load or reuse image
            try:
                img = bpy.data.images.load(path, check_existing=True)
            except Exception as e:
                print(f"Cannot load image: {e}")
                return

            # Find material
            mat = bpy.data.materials.get(material_name)
            if not mat or not mat.use_nodes:
                print(f"Material '{material_name}' not found")
                return

            nt = mat.node_tree
            nodes = nt.nodes

            # Find group node
            group_node = next((n for n in nodes if n.name == 'Group'), None)
            if not group_node:
                print("Group node not found")
                return
            
            # Access the node tree inside the group
            group_tree = group_node.node_tree
            if not group_tree:
                print("Group node has no node tree assigned")
                return
            nodes = group_tree.nodes

            # Create new texture node
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.image = img
            tex_node.label = os.path.basename(path)
            tex_node.location = (300, 200)

            print(f"[Fur] Added Texture node: {img.name}")
            # Automatically trigger use texture callback (material name is the same as name of the object)
            use_prop = f"{material_name}_use_texture"
            setattr(bpy.context.scene, use_prop, True)
        return callback

    # Callback for texture toggle
    def make_use_texture_callback(self, material_name, prop_id):
        def callback(self, context):
            mat = bpy.data.materials.get(material_name)
            if not mat or not mat.use_nodes:
                print(f"Material '{material_name}' not found")
                return

            nt = mat.node_tree
            nodes_prev = nt.nodes

            # Find group node
            group_node = next((n for n in nodes_prev if n.name == 'Group'), None)
            if not group_node:
                print("Group node not found")
                return

            # Access the node tree inside the group
            group_tree = group_node.node_tree
            if not group_tree:
                print("Group node has no node tree assigned")
                return
            
            nodes = group_tree.nodes
            links = group_tree.links
            
            # Find shader node for eevee and hair shader node for cycles
            principleds = [
                n for n in group_tree.nodes
                if (n.bl_idname == 'ShaderNodeBsdfPrincipled' or n.bl_idname == 'ShaderNodeBsdfHairPrincipled')
            ]
            
            # Find texture node
            img_node = next((n for n in nodes if n.type == 'TEX_IMAGE'), None)
            if not img_node:
                print("Texture node not found")
                return

            use = getattr(self, prop_id)
            storage_key = "_saved_base_color_links"
            
            # Apply texture
            if use:
                # Prepare storage dict on the group node
                saved = {}
                for p in principleds:
                    # Color (principled hair shader) or Base color (principled shader) inpud
                    inp = p.inputs[0]

                    # Capture all existing links
                    orig = [(link.from_node.name, link.from_socket.name)
                            for link in inp.links]
                    if orig:
                        saved[p.name] = orig
                        # remove them
                        for link in list(inp.links):
                            links.remove(link)

                    # Link texture
                    links.new(img_node.outputs['Color'], inp)

                # Store JSON on group node
                group_node[storage_key] = json.dumps(saved)
                print(f"Texture linked in; stored original links for {len(saved)} nodes.")

            # Restore previous links
            else:
                # Load saved links
                saved = {}
                if storage_key in group_node:
                    try:
                        saved = json.loads(group_node[storage_key])
                    except:
                        saved = {}

                # Remove texture links
                for p in principleds:
                    inp = p.inputs[0]
                    for link in list(inp.links):
                        if link.from_node == img_node:
                            links.remove(link)

                # Restore original ones
                restored_count = 0
                for p in principleds:
                    inp = p.inputs[0]
                    for from_name, socket_name in saved.get(p.name, []):
                        src = nodes.get(from_name) or group_node.node_tree.nodes.get(from_name)
                        if src:
                            out_sock = src.outputs.get(socket_name)
                            if out_sock:
                                links.new(out_sock, inp)
                                restored_count += 1

                # Clean up storage
                if storage_key in group_node:
                    del group_node[storage_key]

                print(f"Removed texture links and restored {restored_count} original link(s).")

        return callback

    def execute(self, context):

        scene = context.scene
        self.report({'INFO'}, ("Applying fur..."))

        # Get Human mesh
        human_obj = context.object
        if (not human_obj or not human_obj.name == 'Human'):
            self.report({'ERROR'}, "Object Human must be active")
            return {'CANCELLED'}

        # Load fur asset
        blend_relative_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../data/hair/haireditor/fur.blend"))
        object_name = self.hair_asset

        try:
            with bpy.data.libraries.load(blend_relative_path, link=False) as (data_from, data_to):
                if object_name in data_from.objects:
                    data_to.objects = [object_name]
                else:
                    self.report({'ERROR'}, f"Object '{object_name}' not found in blend file.")
                    return {'CANCELLED'}

            hair_obj = data_to.objects[0]
            if hair_obj is not None:
                bpy.context.collection.objects.link(hair_obj)

        except Exception as e:
            self.report({'ERROR'}, f"Failed to load hair object: {str(e)}")
            return {'CANCELLED'}

        # Activate hair object
        bpy.ops.object.select_all(action='DESELECT')
        hair_obj.select_set(True)
        context.view_layer.objects.active = hair_obj

        # Set Human as surface in Hair Curves data settings
        if hair_obj.type == 'CURVES':
            curves_data = hair_obj.data
            if hasattr(curves_data, 'surface'):
                curves_data.surface = human_obj
            else:
                self.report({'WARNING'}, "Curve object has no surface property")
        else:
            self.report({'WARNING'}, f"Object '{object_name}' is not curve!")

        # Parent fur to Human
        hair_obj.parent = human_obj
        hair_obj.matrix_parent_inverse = human_obj.matrix_world.inverted()

        # Define shape properties
        prop_prefix = f"{self.hair_asset}_"
        props = {
            "length": ("Set Hair Curve Profile", "Socket_1", (0.0, 20.0)),
            "density": ("Set Hair Curve Profile", "Socket_0", (0.0, 1.0)),
            "thickness": ("Set Hair Curve Profile", "Input_3", (0.0, 0.003)),
            "frizz": ("Frizz Hair Curves", "Input_3", (0.0,1.0)),
            "roll": ("Roll Hair Curves", "Input_10", (0.0,1.0)),
            "roll_radius": ("Roll Hair Curves", "Input_3", (0.001, 0.1)),
            "roll_length": ("Roll Hair Curves", "Input_2", (0.001, 0.1)),
            "clump": ("Clump Hair Curves", "Input_7", (0.0,1.0)),
            "clump_distance": ("Clump Hair Curves", "Input_9", (0.003, 0.05)),
            "clump_shape": ("Clump Hair Curves", "Input_6", (-1.0,1.0)),
            "clump_tip_spread": ("Clump Hair Curves", "Input_10", (0.0, 0.02)),
            "noise": ("Hair Curves Noise", "Input_3", (0.0, 1.0)),
            "noise_distance": ("Hair Curves Noise", "Input_14", (0.0, 0.1)),
            "noise_scale": ("Hair Curves Noise", "Input_11", (0.0, 20)),
            "noise_shape": ("Hair Curves Noise", "Input_2", (0.0, 1.0)),
            "curl": ("Curl Hair Curves", "Input_2", (0.0, 1.0)),
            "curl_guide_distance": ("Curl Hair Curves", "Input_4", (0.0, 0.1)),
            "curl_radius": ("Curl Hair Curves", "Input_7", (0.0, 0.1)),
            "curl_frequency": ("Curl Hair Curves", "Input_11", (0.0, 20.0)),
            "holes": ("Set Hair Curve Profile", "Socket_2", (0.0, 1.0)),
            "holes_scale": ("Set Hair Curve Profile", "Socket_3", (0.0, 200.0))
        }

        for name, (mod_name, attr, rng) in props.items():
            prop_id = f"{prop_prefix}{name}"
            if not hasattr(scene.__class__, prop_id):
                setattr(
                    scene.__class__,
                    prop_id,
                    bpy.props.FloatProperty(
                        name=name.replace("_", " ").capitalize(),
                        default=hair_obj.modifiers[mod_name][attr],
                        min = rng[0],
                        max =rng[1],
                        update=self.make_update_callback(hair_obj,mod_name, attr,name, rng)
                    )
                )

        # Define material properties
        material_props = {
            "color1": ("Color 1", (0.117, 0.093, 0.047, 1.0)),
            "color2": ("Color 2", (0.031, 0.016, 0.004, 1.0)),
            "color_noise_scale": ("Noise Scale", (0.0, 500.0)),
            "darken_root": ("Darken root", (0.0, 1.0)),
            "root_color_length": ("Root color length", (0.0, 1.0))
        }
        mat = hair_obj.active_material
        if mat and mat.use_nodes:
            material_name = mat.name

            for name, (input_name, rng) in material_props.items():
                prop_id = f"{self.hair_asset}_{name}"
                if not hasattr(scene.__class__, prop_id):
                    # Different behavior for color and number
                    if isinstance(rng, tuple) and len(rng) == 4:
                        prop = bpy.props.FloatVectorProperty(
                            name=name.replace("_", " ").capitalize(),
                            subtype='COLOR',
                            size=4,
                            min=0.0,
                            max=1.0,
                            default=rng,
                            update=self.make_material_callback(material_name, name, input_name, prop_id)
                        )
                    else:
                        prop = bpy.props.FloatProperty(
                            name=name.replace("_", " ").capitalize(),
                            min=rng[0],
                            max=rng[1],
                            default=(rng[0] + rng[1]) / 2,
                            update=self.make_material_callback(material_name, name, input_name, prop_id)
                        )

                    setattr(scene.__class__, prop_id, prop)

        # Define properties for fur texture
        mat = hair_obj.active_material
        if mat and mat.use_nodes:
            material_name = mat.name
            prop_id = f"{prop_prefix}texture_path"
            if not hasattr(bpy.types.Scene, prop_id):
                setattr(
                    bpy.types.Scene,
                    prop_id,
                    bpy.props.StringProperty(
                        name="Fur Texture",
                        description="Path to fur asset texture",
                        subtype='FILE_PATH',
                        default="",
                        update=self.make_texture_callback(material_name, prop_id)
                    )
                )

        prop_id = f"{prop_prefix}use_texture"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.BoolProperty(
                name=prop_id,
                description=f"Use texture on {self.hair_asset}",
                update=self.make_use_texture_callback(material_name, prop_id),
                default=False
                )
            )

        # Property for UI drawer
        prop_id = f"{prop_prefix}fur_asset_open"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.BoolProperty(
                name=prop_id,
                description=f"Toggle drawer for {self.hair_asset}",
                default=False
                )
            )

        # Reselect Human
        human_obj = bpy.data.objects.get("Human")
        if human_obj:
            bpy.ops.object.select_all(action='DESELECT')
            human_obj.select_set(True)
            context.view_layer.objects.active = human_obj
        else:
            self.report({'WARNING'}, "Human object not found in bpy.data.objects")

        # Enable UI in panel
        scene.hair_setup = True

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ApplyFur_Operator)