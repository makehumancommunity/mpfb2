"""Module for convenience methods for hair editor"""

# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Unused -- just a copy of skineditorservices
# ------------------------------------------------------------------------------
"""Useful functions for hair editor"""

import os, bpy, json

from .logservice import LogService
from .locationservice import LocationService

_LOG = LogService.get_logger("services.haireditorservice")

class HairEditorService():
    """The HairEditorService class provides useful functions for the hair editor. All method are static methods."""

    def __init__(self):
        raise RuntimeError("You should not instance HairEditorService. Use its static methods instead.")

    @staticmethod
    def _get_hair_or_fur_blend_path(search_term="hair"):
        user_data_hair = LocationService.get_user_data("hair")
        if os.path.exists(user_data_hair):
            blend = os.path.join(user_data_hair, "haireditor", search_term + ".blend")
            _LOG.debug("User path for " + search_term + " blend", (blend, os.path.exists(blend)))
            if os.path.exists(blend) and os.path.isfile(blend):
                return os.path.realpath(os.path.abspath(blend))

        system_data_hair = LocationService.get_mpfb_data("hair")
        if os.path.exists(system_data_hair):
            blend = os.path.join(system_data_hair, "haireditor", search_term + ".blend")
            _LOG.debug("System path for " + search_term + " blend", (blend, os.path.exists(blend)))
            if os.path.exists(blend) and os.path.isfile(blend):
                _LOG.warn("Falling back to system path for hair blend, should probably move to user data folder.")
                return os.path.realpath(os.path.abspath(blend))

        _LOG.debug("No hair blend found.")
        return None

    @staticmethod
    def get_hair_blend_path():
        """Get the path to the hair blend file.

        Returns:
            str or None: The absolute path to the hair blend file if found, None otherwise.
            The function first checks in the user data directory, then falls back to the system data directory.
        """
        return HairEditorService._get_hair_or_fur_blend_path(search_term="hair")

    @staticmethod
    def get_fur_blend_path():
        """Get the path to the fur blend file.

        Returns:
            str or None: The absolute path to the fur blend file if found, None otherwise.
            The function first checks in the user data directory, then falls back to the system data directory.
        """
        return HairEditorService._get_hair_or_fur_blend_path(search_term="fur")

    @staticmethod
    def is_hair_asset_installed():
        """Check if the hair asset blend file is installed.

        Returns:
            bool: True if the hair blend file exists, False otherwise.
        """
        return HairEditorService.get_hair_blend_path() is not None

    @staticmethod
    def is_fur_asset_installed():
        """Check if the fur asset blend file is installed.

        Returns:
            bool: True if the fur blend file exists, False otherwise.
        """
        return HairEditorService.get_fur_blend_path() is not None

class HairEditorServiceOld():
    @staticmethod
    def load_textures(textures_json_path):
        """Returns albedo and normal texures from JSON file given as argument"""
        return _SKINEDITOR_SERVICE.load_textures(textures_json_path)

    @staticmethod
    def create_texture_nodes(material, textures, location_x, location_y, mix_node_offset):
        """Creates texture nodes and mix nodes for given textures.
            args: material to which nodes are added, List of texture data dictionaries, X and Y position of the first texture node, Offset of nodes."""
        return _SKINEDITOR_SERVICE.create_texture_nodes(material, textures, location_x, location_y, mix_node_offset)

    @staticmethod
    def add_textures_to_scene(scene, albedo_textures, normal_textures):
        """Stores textures in scene properties to be accesible elswhere"""
        return _SKINEDITOR_SERVICE.add_textures_to_scene(scene, albedo_textures, normal_textures)

    @staticmethod
    def add_drawer_to_scene(scene, drawer_name):
        """Used to keep track of opened collapsable panels"""
        return _SKINEDITOR_SERVICE.add_drawer_to_scene(scene, drawer_name)

    @staticmethod
    def find_next_mix_rgb_node(texture_node):
        return _SKINEDITOR_SERVICE.find_next_mix_rgb_node(texture_node)

    @staticmethod
    def add_factor_property(scene, tex_name):
        return _SKINEDITOR_SERVICE.add_factor_property(scene, tex_name)

    @staticmethod
    def make_update_callback(tex_name):
        return _SKINEDITOR_SERVICE.make_update_callback(tex_name)

    @staticmethod
    def add_multiply_factor_property(scene, mix_node):
        return _SKINEDITOR_SERVICE.add_multiply_factor_property(scene, mix_node)

    @staticmethod
    def add_multiply_color_property(scene, mix_node):
        return _SKINEDITOR_SERVICE.add_multiply_color_property(scene, mix_node)

    @staticmethod
    def add_gamma_color_property(scene, mix_node):
        return _SKINEDITOR_SERVICE.add_gamma_color_property(scene, mix_node)

    @staticmethod
    def add_tattoo_influence_property(scene, tattoo_name):
        return _SKINEDITOR_SERVICE.add_tattoo_influence_property(scene, tattoo_name)

    @staticmethod
    def add_tattoo_property(scene):
        return _SKINEDITOR_SERVICE.add_tattoo_property(scene)

    @staticmethod
    def add_freckles_property(scene):
        return _SKINEDITOR_SERVICE.add_freckles_property(scene)

    @staticmethod
    def add_bake_property(scene):
        return _SKINEDITOR_SERVICE.add_bake_property(scene)

    @staticmethod
    def bake_skin_categories(context, texture_resolution, baking_type):
        return _SKINEDITOR_SERVICE.bake_skin_categories(context, texture_resolution, baking_type)

    @staticmethod
    def bake_category(context, texture_categories, categories_to_bake, output_name, texture_resolution, baking_type, base_alpha):
        return _SKINEDITOR_SERVICE.bake_category(context, texture_categories, categories_to_bake, output_name, texture_resolution, baking_type, base_alpha)

    @staticmethod
    def connect_baked_textures_to_shader(self, context, texture_categories):
        return _SKINEDITOR_SERVICE.connect_baked_textures_to_shader(self, context, texture_categories)

class _HairEditorService():

    def __init__(self):
        self._data = {}


    def load_textures(self, textures_json_path):
        """Load texture paths from a JSON file inside the given folder."""

        if not os.path.exists(textures_json_path):
            print("ERROR: Texture JSON file not found at", textures_json_path)
            return None, None

        try:
            with open(textures_json_path, "r", encoding="utf-8") as file:
                texture_data = json.load(file)


            albedo_textures = texture_data.get("albedo", [])
            normal_textures = texture_data.get("normal", [])


            return albedo_textures, normal_textures

        except Exception as e:
            print("ERROR: Failed to load texture JSON:", str(e))
            return None, None


    def create_texture_nodes(self, material, textures, location_x, location_y, mix_node_offset):
        """Creates texture nodes and mix nodes for given textures."""
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        texture_nodes = []
        mix_nodes = []

        # Create texture nodes
        for i, tex_data in enumerate(textures):
            tex = nodes.new(type="ShaderNodeTexImage")
            tex.location = (location_x + i * 300, location_y)
            tex.label = tex_data["label"]

            tex_path = os.path.join(os.path.dirname(__file__), tex_data["path"])
            if os.path.exists(tex_path):
                tex.image = bpy.data.images.load(tex_path)
                if "norm" in tex_data["label"].lower():
                    tex.image.colorspace_settings.name = "Non-Color"
            else:
                print(f"WARNING: Texture {tex_path} not found")

            texture_nodes.append(tex)

        # Create mix nodes
        for i in range(len(textures) - 1):
            mix1 = nodes.new(type="ShaderNodeMixRGB")
            mix1.blend_type = 'MIX'
            mix1.location = (location_x + mix_node_offset + i * 300, location_y + 200)
            mix_nodes.append(mix1)

            mix2 = nodes.new(type="ShaderNodeMixRGB")
            mix2.blend_type = 'MIX'
            mix2.location = (location_x + mix_node_offset + i * 300, location_y - 200)
            mix2.inputs[0].default_value = 0.0
            mix_nodes.append(mix2)

        # First texture connections
        if texture_nodes and mix_nodes:
            links.new(texture_nodes[0].outputs["Color"], mix_nodes[0].inputs[1])  # T1 → M1(A)
            links.new(texture_nodes[0].outputs["Color"], mix_nodes[1].inputs[1])  # T1 → M2(A)

        # Connect textures to mix nodes
        for i in range(len(textures) - 1):
            if i < len(textures) - 1:
                links.new(texture_nodes[i + 1].outputs["Color"], mix_nodes[1 + 2 * i].inputs[2])  # T1 → M2(B)
                links.new(texture_nodes[i + 1].outputs["Alpha"], mix_nodes[2 * i].inputs[0])  # T1(Alpha) → M1(Factor)
                links.new(mix_nodes[1 + 2 * i].outputs["Color"], mix_nodes[2 * i].inputs[2])  # M1 → M2(B)

                if 2 + 2 * i < len(mix_nodes):
                    links.new(mix_nodes[2 * i].outputs["Color"], mix_nodes[2 + 2 * i].inputs[1])  # M1 → next M1(A)
                    links.new(mix_nodes[2 * i].outputs["Color"], mix_nodes[3 + 2 * i].inputs[1])  # M1 → next M2(A)

        return texture_nodes, mix_nodes

    def add_textures_to_scene(self, scene, albedo_textures, normal_textures):
        """Adds drawers, albedo and normal textures into scene properties"""

        scene["textures_data"] = {
            "albedo": albedo_textures,
            "normal": normal_textures
        }

        if "alternative_texture_paths" not in scene:
            scene["alternative_texture_paths"] = {
                "albedo": {},
                "normal": {}
            }


        self.add_tattoo_property(scene)
        self.add_freckles_property(scene)
        self.add_bake_property(scene)


        drawer_names = set()
        for tex in (albedo_textures + normal_textures):
            drawer_names.add(tex.get("drawer", "others"))
            tex_label = tex["label"]

            # Adding factor slider property
            tex_name = os.path.basename(tex.get("label", "N/A"))
            prop_name = self.add_factor_property(scene, tex_name)

            # Adding the alternative paths for each texture
            if "alt_path" in tex:
                alt_paths = tex["alt_path"]

                prop_name = f"alt_texture_{tex_label.replace(' ', '_')}"
                if not hasattr(bpy.types.Scene, prop_name):
                    items = [(str(i), os.path.basename(path), path) for i, path in enumerate(alt_paths)]

                    if items:
                        update_cb = self.alt_texture_update_callback(tex_label, items)

                        setattr(
                            bpy.types.Scene,
                            prop_name,
                            bpy.props.EnumProperty(
                                name=f"Alternative Texture for {tex_label}",
                                description=f"Select alternative texture for {tex_label}",
                                items=items,
                                default=items[0][0] if items else "0",
                                update=update_cb
                            )
                        )
        drawer_names.add("tattoos")
        drawer_names.add("freckles")


        # init drawers
        for drawer_name in drawer_names:
            prop_name = f"drawer_open_{drawer_name}"
            if prop_name not in scene:
                scene[prop_name] = False

        scene["textures_loaded"] = True

    # probably cannot write into scene while drawing
    def add_drawer_to_scene(self, scene, drawer_name):
        """Adds drawer into scene properties"""

        if f"drawer_open_{drawer_name}" not in scene:
            scene[f"drawer_open_{drawer_name}"] = True

    def find_next_mix_rgb_node(self, texture_node):
        """Finds mixRGB node, which controls influence of the given texture on material."""
        if not texture_node:
            return None

        for link in texture_node.id_data.links:
            if link.from_node == texture_node:
                to_node = link.to_node
                if to_node and to_node.type == 'MIX_RGB':
                    # Mix color B pin
                    if link.to_socket.name == 'Color2':
                        return to_node
        return None

    def add_factor_property(self, scene, tex_name):
        """Adds mixRGB factor property to scene."""
        prop_name = f"mix_factor_{tex_name}"

        if not hasattr(bpy.types.Scene, prop_name):
            def update_callback(self, context):
                factor_value = getattr(context.scene, prop_name)

                mat = context.object.active_material
                if mat and mat.node_tree:
                    nodes = mat.node_tree.nodes
                    texture_node = next(
                        #(n for n in nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name == tex_name),
                        (n for n in nodes if n.type == 'TEX_IMAGE' and n.label == tex_name),
                        None
                    )
                    if texture_node:
                        mix_rgb_node = SkinEditorService.find_next_mix_rgb_node(texture_node)
                        if mix_rgb_node:
                            mix_rgb_node.inputs[0].default_value = factor_value

            setattr(
                bpy.types.Scene,
                prop_name,
                bpy.props.FloatProperty(
                    name=f"Influence {tex_name}",
                    description=f"Mix factor for {tex_name}",
                    default=0.0,
                    min=0.0,
                    max=1.0,
                    update=update_callback
                )
            )
        return prop_name

    def update_mix_factor(self, context):
        tex_name = self.get("tex_name", "")
        if tex_name:
            bpy.ops.mpfb.update_mix_factor_operator(tex_name=tex_name)

    def make_update_callback(self,tex_name):
        """Callback for texture influence slider"""
        def update_callback(self, context):
            scene = context.scene
            factor_value = getattr(scene, f"mix_factor_{tex_name}")

            mat = context.object.active_material
            if mat and mat.node_tree:
                nodes = mat.node_tree.nodes
                texture_node = next(
                    #(n for n in nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name == tex_name),
                    (n for n in nodes if n.type == 'TEX_IMAGE' and n.label == tex_name),
                    None
                )
                if texture_node:
                    mix_rgb_node = SkinEditorService.find_next_mix_rgb_node(texture_node)
                    if mix_rgb_node:
                        mix_rgb_node.inputs[0].default_value = factor_value
        return update_callback


    def alt_texture_update_callback(self,tex_label, items):
        """Callback for alternative texture selector"""
        def update_callback(self, context):
            prop_name = f"alt_texture_{tex_label.replace(' ', '_')}"
            selected_index = getattr(context.scene, prop_name)
            selected_path = os.path.join(os.path.dirname(__file__),(items[int(selected_index)][2]))

            obj = context.object
            if not obj or not obj.active_material:
                return
            mat = obj.active_material
            if not mat.node_tree:
                return

            # Get texture node
            texture_node = next(
                (n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.label == tex_label),
                None
            )
            if texture_node:
                try:
                    new_image = bpy.data.images.load(selected_path)
                except Exception as e:
                    print(f"Error in loading texture from: {selected_path}: {e}")
                    return
                texture_node.image = new_image

                # set to non color data in case of normal texture
                if tex_label.endswith('_norm'):
                    texture_node.image.colorspace_settings.name = 'Non-Color'

        return update_callback

    def add_multiply_factor_property(self, scene, mix_node):
        """Adds property for skin color slider"""
        prop_name = "multiply_factor"

        if not hasattr(bpy.types.Scene, prop_name):
            def update_callback(self, context):
                factor_value = getattr(context.scene, prop_name)

                mat = context.object.active_material
                if mat and mat.node_tree:
                    mix_node = next((n for n in mat.node_tree.nodes if n.type == 'MIX_RGB' and n.blend_type == 'MULTIPLY'), None)
                    if mix_node:
                        mix_node.inputs[0].default_value = factor_value

            setattr(
                bpy.types.Scene,
                prop_name,
                bpy.props.FloatProperty(
                    name="Multiply Factor",
                    description="Controls the intensity of the multiply effect for color",
                    default=0.0,
                    min=0.0,
                    max=1.0,
                    update=update_callback
                )
            )

    def add_multiply_color_property(self, scene, mix_node):
        """Adds property for RGB Node color picker"""
        prop_name = "multiply_color"

        if not hasattr(bpy.types.Scene, prop_name):
            def update_callback(self, context):
                color_value = getattr(context.scene, prop_name)

                mat = context.object.active_material
                if mat and mat.node_tree:
                    mix_node = next((n for n in mat.node_tree.nodes if n.type == 'MIX_RGB' and n.blend_type == 'MULTIPLY'), None)
                    if mix_node:
                        mix_node.inputs[2].default_value = (*color_value, 1.0)

            setattr(
                bpy.types.Scene,
                prop_name,
                bpy.props.FloatVectorProperty(
                    name="Multiply Color",
                    description="Color used in Multiply MixRGB Node",
                    subtype="COLOR",
                    default=(1.0, 1.0, 1.0),
                    min=0.0,
                    max=1.0,
                    update=update_callback
                )
            )

    def add_gamma_color_property(self, scene, gamma_node):
        """Adds property for Gamma slider"""
        prop_name = "gamma_value"

        if not hasattr(bpy.types.Scene, prop_name):
            def update_callback(self, context):
                gamma_value = getattr(context.scene, prop_name)

                if gamma_node:
                    gamma_node.inputs[1].default_value = gamma_value

            setattr(
                bpy.types.Scene,
                prop_name,
                bpy.props.FloatProperty(
                    name="Gamma",
                    description="Gamma Correction",
                    default=1.0,
                    min=0.1,
                    max=4.0,
                    update=update_callback
                )
            )

    def add_tattoo_influence_property(self, scene, tattoo_name):
        """Adds property for tattoo influence slider"""

        prop_name = f"tattoo_influence_{tattoo_name}"

        if not hasattr(bpy.types.Scene, prop_name):
            def update_callback(self, context):
                factor_value = getattr(context.scene, prop_name)

                mat = context.object.active_material
                if mat and mat.node_tree:
                    nodes = mat.node_tree.nodes
                    texture_node = next(
                        #(n for n in nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name == tex_name),
                        (n for n in nodes if n.type == 'TEX_IMAGE' and n.label == ("mapped"+tattoo_name)),
                        None
                    )
                    if texture_node:
                        mix_rgb_node = SkinEditorService.find_next_mix_rgb_node(texture_node)
                        if mix_rgb_node:
                            mix_rgb_node.inputs[0].default_value = factor_value

            setattr(
                bpy.types.Scene,
                prop_name,
                bpy.props.FloatProperty(
                    name=f"Influence {tattoo_name}",
                    description=f"Mix factor for {tattoo_name}",
                    default=1.0,
                    min=0.0,
                    max=1.0,
                    update=update_callback
                )
            )


    def add_tattoo_property(self, scene):
        """Adds properties for Tattoo editor"""
        actual_dir = os.path.dirname(__file__)
        default_dir = os.path.join(actual_dir, "../data/textures/skin_editor/tattoo_sources/")
        default_dest = os.path.join(actual_dir, "../data/textures/skin_editor/tattoo_textures/")

        if not hasattr(bpy.types.Scene, "tattoos_editing"):
            bpy.types.Scene.tattoos_editing = bpy.props.BoolProperty(
                name="tattoos editing",
                description="Tattoo editor is active",
                default=False
            )

        if not hasattr(bpy.types.Scene, "tattoo_color_influence"):
            bpy.types.Scene.tattoo_color_influence = bpy.props.BoolProperty(
                name="Skin color influence:",
                description="Do you want your tattoo to be affected by skin color?",
                default=False
            )

        if not hasattr(bpy.types.Scene, "tattoo_texture_path"):
            bpy.types.Scene.tattoo_texture_path = bpy.props.StringProperty(
                name="Tattoo Texture",
                description="Path to a tattoo texture file (drag and drop supported)",
                default=default_dir,
                subtype="FILE_PATH"
            )
        if not hasattr(bpy.types.Scene, "tattoo_texture_destination"):
            bpy.types.Scene.tattoo_texture_destination = bpy.props.StringProperty(
                name="Save destination",
                description="Where do you want to store your tattoo texture?",
                default=default_dest,
                subtype="FILE_PATH"
            )

    def add_freckles_property(self, scene):
        """Adds properties for Freckles"""
        actual_dir = os.path.dirname(__file__)
        default_dest = os.path.join(actual_dir, "../data/textures/skin_editor/tattoo_textures/")

        if not hasattr(bpy.types.Scene, "freckles_applied"):
            bpy.types.Scene.freckles_applied = bpy.props.BoolProperty(
                name="freckles applied",
                description="Are freckles applied?",
                default=False
            )
        if not hasattr(bpy.types.Scene, "freckles_editing"):
            bpy.types.Scene.freckles_editing = bpy.props.BoolProperty(
                name="freckles editing",
                description="Freckles editor is active",
                default=False
            )

        if not hasattr(bpy.types.Scene, "freckles_color"):
            def update_color_callback(self, context):
                color_value = getattr(context.scene, "freckles_color")
                brush = bpy.context.tool_settings.image_paint.brush
                brush.texture.color_ramp.elements[0].color = (*color_value, 1)

            setattr(
                bpy.types.Scene,
                "freckles_color",
                bpy.props.FloatVectorProperty(
                    name="Freckles",
                    description="Color of freckles - can be changed during painting.",
                    subtype="COLOR",
                    default=(0.6, 0.1, 0.1),
                    min=0.0,
                    max=1.0,
                    update=update_color_callback
                )
            )

        if not hasattr(bpy.types.Scene, "voronoi_size"):
            def update_size_callback(self, context):
                size_value = getattr(context.scene, "voronoi_size")
                brush = bpy.context.tool_settings.image_paint.brush
                brush.texture.noise_scale = size_value

            setattr(
                bpy.types.Scene,
                "voronoi_size",
                bpy.props.FloatProperty(
                    name="voronoi_size",
                    description="Size of freckles texture - can be changed during painting.",
                    default=0.15,
                    min=0.0,
                    max=2.0,
                    update=update_size_callback
                )
            )
        if not hasattr(bpy.types.Scene, "voronoi_intensity"):
            def update_intensity_callback(self, context):
                size_value = getattr(context.scene, "voronoi_intensity")
                #TODO: find right freckles value
                brush = bpy.context.tool_settings.image_paint.brush
                brush.texture.noise_intensity = size_value

            setattr(
                bpy.types.Scene,
                "voronoi_intensity",
                bpy.props.FloatProperty(
                    name="voronoi_intensity",
                    description="Intensity of freckles texture - can be changed during painting.",
                    default=5.0,
                    min=0.0,
                    max=10.0,
                    update=update_intensity_callback
                )
            )

        if not hasattr(bpy.types.Scene, "freckles_texture_destination"):
            bpy.types.Scene.freckles_texture_destination = bpy.props.StringProperty(
                name="Save destination",
                description="Where do you want to store your freckles texture?",
                default=default_dest,
                subtype="FILE_PATH"
            )

    def add_bake_property(self, scene):
        """Adds properties for Freckles"""
        actual_dir = os.path.dirname(__file__)
        default_dest = os.path.join(actual_dir, "../data/textures/skin_editor/tattoo_textures/")

        if not hasattr(bpy.types.Scene, "bake_muscles"):
            bpy.types.Scene.bake_muscles = bpy.props.BoolProperty(
                name="bake_muscles",
                description="Do you want to bake muscle textures to final material or keep them separate?",
                default=True
            )
        if not hasattr(bpy.types.Scene, "bake_wrinkles"):
            bpy.types.Scene.bake_wrinkles = bpy.props.BoolProperty(
                name="bake_wrinkles",
                description="Do you want to bake wrinkles textures to final material or keep them separate?",
                default=True
            )
        if not hasattr(bpy.types.Scene, "bake_tattoos"):
            bpy.types.Scene.bake_tattoos = bpy.props.BoolProperty(
                name="bake_tattoos",
                description="Do you want to bake tattoo textures to final material or keep them separate?",
                default=True
            )
        if not hasattr(bpy.types.Scene, "bake_freckles"):
            bpy.types.Scene.bake_freckles = bpy.props.BoolProperty(
                name="bake_freckles",
                description="Do you want to bake freckles texture to final material or keep it separate?",
                default=True
            )
        if not hasattr(bpy.types.Scene, "bake_others"):
            bpy.types.Scene.bake_others = bpy.props.BoolProperty(
                name="bake_others",
                description="Do you want to bake texture category \"others\" to final material or keep them separate?",
                default=True
            )
        if not hasattr(bpy.types.Scene, "bake_color"):
            bpy.types.Scene.bake_color = bpy.props.BoolProperty(
                name="bake_color",
                description="Do you want to bake skin color to the skin texture?",
                default=True
            )
        if not hasattr(bpy.types.Scene, "bake_with_gpu"):
            bpy.types.Scene.bake_with_gpu = bpy.props.BoolProperty(
                name="bake_with_gpu",
                description="GPU baking is faster, but potencially less stable.",
                default=False
            )
        if not hasattr(bpy.types.Scene, "bake_at_once"):
            bpy.types.Scene.bake_at_once = bpy.props.BoolProperty(
                name="bake_at_once",
                description="This will bake diffuse and normal textures in one operation. It is faster, but you won't be able to save your file inbetween.",
                default=False
            )
        if not hasattr(bpy.types.Scene, "diffuse_baked"):
            bpy.types.Scene.diffuse_baked = bpy.props.BoolProperty(
                name="diffuse_baked",
                description="Diffuse textures have been baked.",
                default=False
            )
        if not hasattr(bpy.types.Scene, "normal_baked"):
            bpy.types.Scene.normal_baked = bpy.props.BoolProperty(
                name="normal_baked",
                description="Normal textures have been baked.",
                default=False
            )
        if not hasattr(bpy.types.Scene, "material_baked"):
            bpy.types.Scene.material_baked = bpy.props.BoolProperty(
                name="material_baked",
                description="Both diffuse and normal textures have been baked.",
                default=False
            )


        if not hasattr(bpy.types.Scene, "bake_texture_destination"):
            bpy.types.Scene.bake_texture_destination = bpy.props.StringProperty(
                name="Save destination",
                description="Where do you want to store your baked textures?",
                default=default_dest,
                subtype="FILE_PATH"
            )

    def bake_skin_categories(self, context, texture_resolution, baking_type):
        scene = context.scene

        # Load texture data
        textures_data = scene.get("textures_data", {})
        all_textures = textures_data.get("albedo", []) + textures_data.get("normal", [])

        # Group textures by category
        texture_categories = {
            "base": [],
            "muscles": [],
            "wrinkles": [],
            "others": [],
            "tattoos": [],
            "freckles": [],
        }

        for texture in all_textures:
            category = texture.get("drawer", "others")
            if category in texture_categories:
                texture_categories[category].append(texture)

        # Get tattoo texture names
        for prop in dir(scene):
            if prop.startswith("tattoo_influence_"):
                tattoo_name = prop[len("tattoo_influence_"):]
                texture_categories["tattoos"].append({"label": tattoo_name})  # No direct path, need to fetch later

        # Freckles always have one texture
        if(scene.freckles_applied):
            texture_categories["freckles"].append({"label": "freckles"})

        # Get baking options
        bake_options = {
            "muscles": scene.bake_muscles,
            "wrinkles": scene.bake_wrinkles,
            "tattoos": scene.bake_tattoos,
            "freckles": scene.bake_freckles,
            "others": scene.bake_others,
            "color": scene.bake_color,
        }

        # eventualy turn off color and gama influence
        orig_multiply_factor = scene.multiply_factor
        orig_gamma_value = scene.gamma_value
        if(not bake_options['color']):
            scene.multiply_factor = 0.0
            scene.gamma_value = 1.0

        # Determine categories to bake with base
        base_baking_categories = ["base"] + [cat for cat, should_bake in bake_options.items() if should_bake]
        separate_baking_categories = [cat for cat in texture_categories.keys() if cat not in base_baking_categories and texture_categories[cat]]

        # Get base and freckles nodes for turning off later
        obj = context.object
        if not obj or not obj.active_material:
            print("No active material found.")
            return
        mat = obj.active_material
        node_tree = mat.node_tree
        nodes = node_tree.nodes

        base_texture_node = None
        base_norm_node =None
        freckles_node=None
        for node in nodes:
            #TODO: hint user in json that base must exist and not to name things freckles
            if(node.name == "Freckles Mix"):
                freckles_node = node
            if node.label == "base_diffuse":
                base_texture_node = node
            if node.label =="base_norm":
                base_norm_node = node

        # Eventualy turn off freckles
        if (freckles_node and not scene.bake_freckles):
            freckles_node.inputs[0].default_value = 0.0

        # Bake base with selected categories
        self.bake_category(context, texture_categories, base_baking_categories, "base_baked", texture_resolution, baking_type)


        # Swap base texture for pure alpha texture and disable freckles
        alpha_texture_path = os.path.join(os.path.dirname(__file__), "../data/textures/skin_editor/alpha_textures", texture_resolution + ".png")
        if not os.path.exists(alpha_texture_path):
            print(f"Alpha texture {texture_resolution} not found.")
            return



        if (base_texture_node and base_norm_node):
            alpha_image = bpy.data.images.load(alpha_texture_path)
            base_texture_node.image = alpha_image
            base_texture_node.image.name = "alpha_texture"
            base_norm_node.image=alpha_image
            base_norm_node.image.name = "alpha_texture"

        # Bake remaining categories separately
        for category in separate_baking_categories:
            self.bake_category(context, texture_categories, [category], f"{category}_baked", texture_resolution, baking_type, base_alpha=True)

        # Connect All Baked Textures to Shader**
        self.connect_baked_textures_to_shader(context, texture_categories)


        # Restore base textures
        if (base_texture_node and base_norm_node):
            base_texture_node.image = bpy.data.images.get("base_diffuse.png")
            base_norm_node.image = bpy.data.images.get("base_norm.png")

        # Restore freckles
        if (freckles_node):
            freckles_node.inputs[0].default_value = 1.0

        # Restore color and gamma values
        scene.multiply_factor = orig_multiply_factor
        scene.gamma_value = orig_gamma_value



        #TODO: remove black textures
        #TODO: freckles are baked wrong, but u can use saved texture
    def bake_category(self, context, texture_categories, categories_to_bake, output_name, texture_resolution, baking_type, base_alpha=False):
        """ Helper function to bake a specific set of texture categories """
        scene = context.scene
        obj = context.object
        if not obj or not obj.active_material:
            print("No active material found.")
            return

        dest_dir = scene.bake_texture_destination
        os.makedirs(dest_dir, exist_ok=True)

        mat = obj.active_material
        node_tree = mat.node_tree
        nodes = node_tree.nodes
        links = node_tree.links

        # Load empty alpha texture
        texture_path = os.path.join(os.path.dirname(__file__), "../data/textures/skin_editor/alpha_textures", texture_resolution + ".png")
        if not os.path.exists(texture_path):
            print(f"Texture {texture_resolution} not found.")
            return


        # Disable unwanted textures by setting influence to 0 and save original values
        original_mix_factors = {}
        for category, textures in texture_categories.items():
            if category not in categories_to_bake:
                for texture in textures:
                    mix_factor_prop = f"mix_factor_{texture['label']}"
                    if (not hasattr(scene, mix_factor_prop)):
                        mix_factor_prop = f"tattoo_influence_{texture['label']}"
                    if hasattr(scene, mix_factor_prop):
                        original_mix_factors[mix_factor_prop] = getattr(scene, mix_factor_prop)
                        setattr(scene, mix_factor_prop, 0.0)



        # Are there textures to bake?
        has_diffuse = any(tex for cat in categories_to_bake for tex in texture_categories[cat] if not tex["label"].endswith("_norm"))
        has_normal = any(tex for cat in categories_to_bake for tex in texture_categories[cat] if tex["label"].endswith("_norm"))

        # Setup render settings
        resolution_map = {
                "1K": 1024,
                "2K": 2048,
                "4K": 4096,
                "8K": 8192
            }
        res = resolution_map.get(texture_resolution, 2048)
        scene.render.resolution_x = res
        scene.render.resolution_y = res
        scene.render.resolution_percentage = 100

        scene.render.use_compositing = True
        scene.render.image_settings.file_format = 'PNG'

        scene.use_nodes = True
        comp_tree = scene.node_tree
        comp_nodes = comp_tree.nodes
        comp_links = comp_tree.links

        # Remove all existing compositor nodes.
        for node in comp_nodes:
            comp_nodes.remove(node)

        # Bake Diffuse
        if baking_type != "normal" and has_diffuse:
            if(not base_alpha):
                image = bpy.data.images.load(texture_path)
                texture_node = nodes.new(type="ShaderNodeTexImage")
                texture_node.image = image
                texture_node.label = output_name
                image.name = output_name
                node_tree.nodes.active = texture_node

                bpy.ops.object.bake(type='DIFFUSE')
            else:
                # Other texture groups cannot be baked because of the Blender alpha baking bug
                # (transparent parts would turn black). They need to be put together through the compositor with alpha over as influence
                # Source textures need to be resized to work correctly in compositor
                # Texture retrieving problems solved by directly saving from render


                # Save baked texture destinations
                save_path = os.path.join(dest_dir, f"{output_name}.png")
                # Render settings
                scene.render.filepath = save_path


                # Create a list of all diffuse textures from the categories to bake.
                diffuse_textures = []
                for cat in categories_to_bake:
                    for tex in texture_categories[cat]:
                        if not tex["label"].endswith("_norm"):
                            diffuse_textures.append(tex)

                if not diffuse_textures:
                    print("Error: No diffuse textures found for base_alpha bake")
                    return

                # Stores the last node in the chain
                previous = None

                result_image = bpy.data.images.new(name=output_name, width=res, height=res)

                # Load textures from shader editor or load them from path
                for i, tex in enumerate(diffuse_textures):
                    img_node_found = None
                    for node in nodes:
                        if (node.label == tex["label"] or node.label == 'mapped'+tex["label"]):
                            img_node_found = node
                            break

                    if img_node_found and img_node_found.image:
                        print(f"Found texture {img_node_found.label}")
                        print(f"with image {img_node_found.image.name}")
                        tex_image = img_node_found.image
                    else:
                        print(f"Error: Could not find {tex['label']} in shader editor - Skipping")
                        continue
                    if tex_image and tex_image.size[0] > 0 and tex_image.size[1] > 0:
                        tex_image.alpha_mode = 'STRAIGHT'
                        tex_image.colorspace_settings.name = 'sRGB'
                        img_node = comp_nodes.new(type="CompositorNodeImage")
                        img_node.image = tex_image
                        img_node.location = (-400, -300 * i)
                    else:
                        print(f"Error: {tex['label']} has no valid data - Skipping")
                        continue


                    # Set Alpha node
                    set_alpha = comp_nodes.new(type="CompositorNodeSetAlpha")
                    set_alpha.location = (-100, -300 * i)
                    if(img_node_found.label.startswith('mapped')):
                        mix_factor = getattr(scene, f"tattoo_influence_{tex['label']}", 0.0)
                    else:
                        mix_factor = getattr(scene, f"mix_factor_{tex['label']}", 0.0)
                    set_alpha.inputs["Alpha"].default_value = mix_factor
                    comp_links.new(img_node.outputs["Image"], set_alpha.inputs["Image"])

                    # Calculate scale factor - image wont bake if source image is bigger than render resolution
                    texture_width = tex_image.size[0]
                    if texture_width > res:
                        scale_factor = res / texture_width
                    else:
                        scale_factor = 1.0

                    # Create a Scale node after Set Alpha node
                    scale_node = comp_nodes.new(type="CompositorNodeScale")
                    scale_node.space = 'RELATIVE'
                    scale_node.location = (0, -300 * i)
                    scale_node.inputs["X"].default_value = scale_factor
                    scale_node.inputs["Y"].default_value = scale_factor
                    comp_links.new(set_alpha.outputs["Image"], scale_node.inputs["Image"])

                    # Multiply color node
                    multiply_node = comp_nodes.new(type="CompositorNodeMixRGB")
                    multiply_node.blend_type = 'MULTIPLY'
                    multiply_node.location = (200, -300 * i)
                    multiply_node.inputs["Fac"].default_value = getattr(scene, "multiply_factor", 1.0)
                    multiply_color = getattr(scene, "multiply_color", (1.0, 1.0, 1.0))
                    multiply_color = (*multiply_color, 1.0) # Alpha channel needs to be added
                    multiply_node.inputs[2].default_value = multiply_color
                    comp_links.new(scale_node.outputs["Image"], multiply_node.inputs[1])

                    # if texture is tattoo and not color influenced (has mix node between gamma node and shader node), set factor to 0
                    #FIXME: TATTOOOS ARE BAKED TO THE BASE TEXTURE EVEN WHEN THEY SHOULDNT
                    if(img_node_found.label.startswith('mapped')):
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                prev_node = node.inputs['Base Color'].links[0].from_node
                                while(prev_node.name != 'Gamma'):
                                    if(prev_node.label == f"{tex['label']}"):
                                        multiply_node.inputs["Fac"].default_value = 0.0
                                        break
                                    else:
                                        prev_node = prev_node.inputs["Color1"].links[0].from_node
                                break

                    # Gamma correction node
                    gamma_node = comp_nodes.new(type="CompositorNodeGamma")
                    gamma_node.location = (400, -300 * i)
                    gamma_node.inputs["Gamma"].default_value = getattr(scene, "gamma_value", 1.0)
                    comp_links.new(multiply_node.outputs["Image"], gamma_node.inputs["Image"])


                    # Connect textures using Alpha Over nodes
                    if previous is None:
                        previous = gamma_node
                    else:
                        alpha_over = comp_nodes.new(type="CompositorNodeAlphaOver")
                        alpha_over.location = (200, -300 * i)
                        comp_links.new(previous.outputs["Image"], alpha_over.inputs[1])
                        comp_links.new(gamma_node.outputs["Image"], alpha_over.inputs[2])
                        previous = alpha_over


                # The last alpha over node is the final composite result
                final_node = previous

                # Create Composite output node
                composite_out = comp_nodes.new(type="CompositorNodeComposite")
                composite_out.location = (400, 0)
                comp_links.new(final_node.outputs["Image"], composite_out.inputs["Image"])
                comp_tree.nodes.active = composite_out

                # Render image
                bpy.ops.render.render(use_viewport=False, write_still=True)
                if os.path.exists(save_path):
                    print(f"Render saved to: {save_path}")
                else:
                    print("Error: Rendered image not found")

                # Reload image back to shader editor
                result_image = bpy.data.images.load(save_path)
                texture_node = nodes.new(type="ShaderNodeTexImage")
                texture_node.image = result_image
                texture_node.label = output_name
                node_tree.nodes.active = texture_node



        # Bake Normal
        if baking_type != "diffuse" and has_normal:
            if(not base_alpha):
                image = bpy.data.images.load(texture_path)
                texture_node = nodes.new(type="ShaderNodeTexImage")
                texture_node.image = image
                image.name = output_name + '_norm'
                texture_node.label = output_name + '_norm'
                node_tree.nodes.active = texture_node
                texture_node.image.colorspace_settings.name = 'Non-Color'

                bpy.ops.object.bake(type='NORMAL')

                # Save baked normal
                dest_dir = scene.bake_texture_destination
                save_path = os.path.join(dest_dir, f"{output_name}_norm.png")
                image.filepath_raw = save_path
                image.file_format = 'PNG'
                image.save()

            else:
                # Save baked texture destinations
                save_path = os.path.join(dest_dir, f"{output_name}_norm.png")
                scene.render.filepath = save_path

                # Create a list of all norm textures from the categories to bake.
                norm_textures = []
                for cat in categories_to_bake:
                    for tex in texture_categories[cat]:
                        if tex["label"].endswith("_norm"):
                            norm_textures.append(tex)

                if not norm_textures:
                    print("Error: No norm textures found for base_alpha bake")
                    return

                # Stores the last node in the chain
                previous = None

                # Setup render resolution
                result_image = bpy.data.images.new(name=output_name + '_norm', width=res, height=res)

                # Load textures from shader editor or load them from path
                for i, tex in enumerate(norm_textures):
                    img_node_found = None
                    for node in nodes:
                        if (node.label == tex["label"] or node.label == 'mapped'+tex["label"]):
                            img_node_found = node
                            break

                    if img_node_found and img_node_found.image:
                        print(f"Found texture {img_node_found.label}")
                        print(f"with image {img_node_found.image.name}")
                        tex_image = img_node_found.image
                    else:
                       print(f"Could not find {tex['label']} in shader editor - Skipping")
                    if tex_image and tex_image.size[0] > 0 and tex_image.size[1] > 0:
                        tex_image.alpha_mode = 'STRAIGHT'
                        tex_image.colorspace_settings.name = 'sRGB'
                        img_node = comp_nodes.new(type="CompositorNodeImage")
                        img_node.image = tex_image
                        img_node.location = (-400, -300 * i)
                    else:
                        print(f"Error: {tex['label']} has no valid data - Skipping")
                        continue


                    # Set Alpha node
                    set_alpha = comp_nodes.new(type="CompositorNodeSetAlpha")
                    set_alpha.location = (-100, -300 * i)
                    if(img_node_found.label.startswith('mapped')):
                        mix_factor = getattr(scene, f"tattoo_influence_{tex['label']}", 0.0)
                    else:
                        mix_factor = getattr(scene, f"mix_factor_{tex['label']}", 0.0)
                    set_alpha.inputs["Alpha"].default_value = mix_factor
                    comp_links.new(img_node.outputs["Image"], set_alpha.inputs["Image"]) # add mapped if it is tattoo

                    # Calculate scale factor - image wont bake if source image is bigger than render resolution
                    texture_width = tex_image.size[0]
                    if texture_width > res:
                        scale_factor = res / texture_width
                    else:
                        scale_factor = 1.0

                    # Create a Scale node after Set Alpha node
                    scale_node = comp_nodes.new(type="CompositorNodeScale")
                    scale_node.space = 'RELATIVE'
                    scale_node.location = (0, -300 * i)
                    scale_node.inputs["X"].default_value = scale_factor
                    scale_node.inputs["Y"].default_value = scale_factor
                    comp_links.new(set_alpha.outputs["Image"], scale_node.inputs["Image"])

                    # Connect textures using Alpha Over nodes
                    if previous is None:
                        previous = scale_node
                    else:
                        alpha_over = comp_nodes.new(type="CompositorNodeAlphaOver")
                        alpha_over.location = (200, -300 * i)
                        comp_links.new(previous.outputs["Image"], alpha_over.inputs[1])
                        comp_links.new(scale_node.outputs["Image"], alpha_over.inputs[2])
                        previous = alpha_over


                # The last alpha over node is the final composite result
                final_node = previous

                # Create Composite output node
                composite_out = comp_nodes.new(type="CompositorNodeComposite")
                composite_out.location = (400, 0)
                comp_links.new(final_node.outputs["Image"], composite_out.inputs["Image"])
                comp_tree.nodes.active = composite_out

                # Render image
                bpy.ops.render.render(use_viewport=False, write_still=True)
                if os.path.exists(save_path):
                    print(f"Render saved to: {save_path}")
                else:
                    print("Error: Rendered image not found")

                # Reload image back to shader editor
                result_image = bpy.data.images.load(save_path)
                texture_node = nodes.new(type="ShaderNodeTexImage")
                texture_node.image = result_image
                texture_node.label = output_name + '_norm'
                node_tree.nodes.active = texture_node


        # Restore texture influences
        for mix_factor_prop, original_value in original_mix_factors.items():
            setattr(scene, mix_factor_prop, original_value)
            pass

        print(f"{output_name} baked successfully!")

    def connect_baked_textures_to_shader(self, context, texture_categories):

        scene = context.scene
        obj = context.object
        if not obj or not obj.active_material:
            print("No active material found for linking baked textures.")
            return

        mat = obj.active_material
        node_tree = mat.node_tree
        nodes = node_tree.nodes
        links = node_tree.links

        # Expected baked diffuse and normal node labels.
        diffuse_names = ["base_baked", "muscles_baked", "wrinkles_baked", "tattoos_baked", "freckles_baked", "others_baked"]
        normal_names = ["base_baked_norm", "muscles_baked_norm", "wrinkles_baked_norm", "tattoos_baked_norm", "freckles_baked_norm", "others_baked_norm"]

        # Retrieve existing diffuse texture nodes based on label.
        baked_diffuse_nodes = []
        for name in diffuse_names:
            for node in nodes:
                if node.type == "TEX_IMAGE" and node.label == name:
                    baked_diffuse_nodes.append(node)
                    break

        # Chain diffuse textures with MixRGB nodes.
        if baked_diffuse_nodes:
            current_output = baked_diffuse_nodes[0].outputs['Color']
            for node in baked_diffuse_nodes[1:]:
                mix_node = nodes.new(type="ShaderNodeMixRGB")
                mix_node.blend_type = 'MIX'
                alpha_output = node.outputs.get('Alpha')
                links.new(current_output, mix_node.inputs[1])
                links.new(node.outputs['Color'], mix_node.inputs[2])
                if alpha_output:
                    links.new(alpha_output, mix_node.inputs['Fac'])
                if(node.label == "freckles_baked"):
                    node.image = bpy.data.images.load(scene.freckles_texture_destination+"freckles.png")
                current_output = mix_node.outputs['Color']

            # Connect the final diffuse mix to the Principled BSDF's Base Color.
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    links.new(current_output, node.inputs['Base Color'])
                    break

        # Retrieve existing normal texture nodes based on label.
        baked_normal_nodes = []
        for name in normal_names:
            for node in nodes:
                if node.type == "TEX_IMAGE" and node.label == name:
                    node.image.colorspace_settings.name = 'Non-Color'
                    baked_normal_nodes.append(node)
                    break

        # Chain normal textures.
        if baked_normal_nodes:
            current_output = baked_normal_nodes[0].outputs['Color']
            for node in baked_normal_nodes[1:]:
                mix_node = nodes.new(type="ShaderNodeMixRGB")
                mix_node.blend_type = 'MIX'
                alpha_output = node.outputs.get('Alpha')
                links.new(current_output, mix_node.inputs[1])
                links.new(node.outputs['Color'], mix_node.inputs[2])
                if alpha_output:
                    links.new(alpha_output, mix_node.inputs['Fac'])
                current_output = mix_node.outputs['Color']

            # Create a Normal Map node to interpret the mixed normal map.
            normal_map_node = nodes.new(type="ShaderNodeNormalMap")
            normal_map_node.inputs['Strength'].default_value = 1.0
            links.new(current_output, normal_map_node.inputs['Color'])
            # Connect the normal map to the Principled BSDF's Normal input.
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    links.new(normal_map_node.outputs['Normal'], node.inputs['Normal'])
                    break

        print("Baked textures connected successfully!")

_HAIREDITOR_SERVICE = _HairEditorService()
