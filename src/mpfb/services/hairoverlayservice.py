# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         19.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  building a shader out of the baked hair maps, and blending it over a skin material
# ------------------------------------------------------------------------------
"""Shared shader building for the baked hair maps, used by the card/body shell materials and by the "Body texture" overlay."""

import bpy

from .logservice import LogService

_LOG = LogService.get_logger("services.hairoverlayservice")

# Marks every node added to a skin material so the overlay can be removed again. The value is the asset name
OVERLAY_TAG = "mpfb_fur_overlay"

# Marks nodes the panel exposes to the user after a bake. The value is the role
ROLE_TAG = "mpfb_fur_role"

ROLE_ALPHA_RAMP = "alpha_ramp"

ROLE_SHADER = "shader"

ROLE_EDGE_FADE = "edge_fade"

ROLE_DEPTH_CUTOFF = "depth_cutoff"

ROLE_SIDE_ON_CUTOFF = "side_on_cutoff"

ROLE_SIDE_ON_TIPS = "side_on_tips"


class HairOverlayService():
    """Shaders made of the baked hair maps, for the baked materials and for the body texture overlay. All methods are static methods."""

    def __init__(self) -> None:
        raise RuntimeError("You should not instance HairOverlayService. Use its static methods instead.")

    @staticmethod
    def build_fur_shader(node_tree: bpy.types.NodeTree, images: dict[str, bpy.types.Image], location: tuple[float, float] = (0, 0)) -> tuple[bpy.types.NodeSocket, bpy.types.NodeSocket, list[bpy.types.Node]]:
        """Nodes turning the baked maps into a shader.

        Returns (shader_socket, alpha_socket, created_nodes). ``images`` maps map keys ("color",
        "normal", "ao", ...) to image datablocks; only "color" is mandatory.

        Map connections:

            color       Base Color, and its alpha to Alpha
            ao          multiplied into Base Color
            normal      Normal, through a Normal Map node set to object space
            root/tip    Roughness, through a Map Range
            flow        Tangent, with Anisotropic raised off zero

        Depth is added as an unconnected node, no Principled input uses it (it is meant for eventual external engine).
        The alpha goes through a Color Ramp, which the panel exposes to tune transparency.
        """
        nodes = node_tree.nodes
        links = node_tree.links
        x, y = location
        created = []

        def add(idname, offset, label=None, role=None):
            node = nodes.new(idname)
            node.location = (x + offset[0], y + offset[1])
            if label:
                node.label = label
            if role:
                node[ROLE_TAG] = role
            created.append(node)
            return node

        def texture(key, offset, label):
            node = add('ShaderNodeTexImage', offset, label)
            node.image = images[key]
            return node

        bsdf = add('ShaderNodeBsdfPrincipled', (600, 0), role=ROLE_SHADER)
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 1.0

        color_texture = texture("color", (0, 200), "Hair colour")
        base_color = color_texture.outputs['Color']

        # Alpha levels control, identity mapping until the user moves a stop
        alpha_ramp = add('ShaderNodeValToRGB', (300, 400), "Hair alpha levels", role=ROLE_ALPHA_RAMP)
        links.new(color_texture.outputs['Alpha'], alpha_ramp.inputs['Fac'])
        alpha = alpha_ramp.outputs['Color']

        if images.get("ao") is not None:
            ao_texture = texture("ao", (0, -100), "Hair AO")
            multiply = add('ShaderNodeMix', (300, 100))
            multiply.data_type = 'RGBA'
            multiply.blend_type = 'MULTIPLY'
            multiply.inputs[0].default_value = 1.0  # Factor
            links.new(base_color, multiply.inputs[6])  # A (color variant)
            links.new(ao_texture.outputs['Color'], multiply.inputs[7])  # B (color variant)
            base_color = multiply.outputs[2]  # Result (color variant)

        links.new(base_color, bsdf.inputs['Base Color'])

        if images.get("normal") is not None:
            normal_texture = texture("normal", (0, -400), "Hair normal (object space)")
            normal_map = add('ShaderNodeNormalMap', (300, -400))
            # The bake cannot produce a tangent space map through a ray portal, so the map is in object space
            normal_map.space = 'OBJECT'
            links.new(normal_texture.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

        if images.get("root_tip") is not None:
            root_tip_texture = texture("root_tip", (0, -700), "Hair root/tip")
            # Black at the root, white at the tip, so To Min is the root roughness and To Max the tip roughness
            roughness = add('ShaderNodeMapRange', (300, -700), "Root/tip to roughness")
            roughness.inputs['To Min'].default_value = 1.0
            roughness.inputs['To Max'].default_value = 0.5
            links.new(root_tip_texture.outputs['Color'], roughness.inputs['Value'])
            links.new(roughness.outputs['Result'], bsdf.inputs['Roughness'])

        if images.get("flow") is not None:
            flow_texture = texture("flow", (0, -1000), "Hair flow (object space)")
            links.new(flow_texture.outputs['Color'], bsdf.inputs['Tangent'])
            # Tangent has no effect without anisotropy
            bsdf.inputs['Anisotropic'].default_value = 0.4

        if images.get("depth") is not None:
            # No Principled input for depth, left unconnected
            texture("depth", (0, -1300), "Hair depth (for the engine, no blender input)")

        return bsdf.outputs['BSDF'], alpha, created

    @staticmethod
    def find_tagged_node(node_tree: bpy.types.NodeTree | None, role: str, asset_name: str | None = None) -> bpy.types.Node | None:
        """The node this module added for ``role``, or None. Found by tag, since the skin material has other nodes too."""
        if node_tree is None:
            return None
        for node in node_tree.nodes:
            if node.get(ROLE_TAG) != role:
                continue
            if asset_name is not None and node.get(OVERLAY_TAG) not in (None, asset_name):
                continue
            return node
        return None

    @staticmethod
    def build_baked_material(name: str, images: dict[str, bpy.types.Image], edge_fade_attribute: str | None = None) -> bpy.types.Material:
        """A standalone material showing only the baked hair, for the cards and the body shell.

        ``edge_fade_attribute`` optionally names a per-vertex 0..1 weight to multiply into the alpha (soft edge of the body shell).
        A baked depth map also gets wired into the alpha as a cutoff, with the threshold at zero it does nothing.
        """
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        material.node_tree.nodes.clear()

        output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        output.location = (900, 0)
        shader, alpha, _created = HairOverlayService.build_fur_shader(material.node_tree, images)
        material.node_tree.links.new(shader, output.inputs['Surface'])

        if images.get("depth") is not None:
            alpha = HairOverlayService._multiply_in_depth_cutoff(material.node_tree, alpha, images["depth"])
        if images.get("side_on") is not None:
            alpha = HairOverlayService._multiply_in_side_on_cutoff(material.node_tree, alpha, images)
        if edge_fade_attribute:
            alpha = HairOverlayService._multiply_in_edge_fade(material.node_tree, alpha, edge_fade_attribute)

        # Cards and shell have to be transparent where there is no hair
        principled = next(n for n in material.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
        material.node_tree.links.new(alpha, principled.inputs['Alpha'])
        if hasattr(material, "blend_method"):
            material.blend_method = 'BLEND'
        if hasattr(material, "use_backface_culling"):
            # Cards are single-sided, culling would make them disappear when seen from behind
            material.use_backface_culling = False
        return material

    @staticmethod
    def _bounded_factor(nodes: bpy.types.Nodes, label: str, location: tuple[float, float], role: str | None = None, default: float = 0.0) -> tuple[bpy.types.Node, bpy.types.NodeSocket]:
        """A 0..1 control. Returns (node, output socket).

        Mix Factor is used because blender draws it as a 0..1 slider, a plain Math input would be unbounded.
        """
        node = nodes.new('ShaderNodeMix')
        node.data_type = 'FLOAT'
        node.label = label
        node.location = location
        if hasattr(node, "clamp_factor"):
            node.clamp_factor = True
        node.inputs[0].default_value = default
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 1.0
        if role:
            node[ROLE_TAG] = role
        return node, node.outputs[0]

    @staticmethod
    def _multiply_in_side_on_cutoff(node_tree: bpy.types.NodeTree, alpha_socket: bpy.types.NodeSocket, images: dict[str, bpy.types.Image]) -> bpy.types.NodeSocket:
        """Hide texels whose hair was captured end-on. Returns the gated alpha socket.

        The side-on map holds 1 - |dot(strand tangent, ray direction)|: white where the strand crossed the capture ray,
        black where the ray looked straight down its length.
        The angle alone selects too much, so the root/tip map is weighed in, as the undesired artifacts are usualy at the hair ends:

            score = (side_on + tip_weight*(1 - root_tip)) / (1 + tip_weight)

        Texels with score below the threshold are hidden. With threshold 0 the chain does nothing.
        """
        nodes = node_tree.nodes
        links = node_tree.links

        side_on_image = images.get("side_on")
        if side_on_image is None:
            return alpha_socket

        def texture_for(image, label, location):
            """The image texture node, created if the shader has none."""
            existing = next((node for node in nodes
                             if node.bl_idname == 'ShaderNodeTexImage' and node.image == image), None)
            if existing is not None:
                return existing
            node = nodes.new('ShaderNodeTexImage')
            node.image = image
            node.label = label
            node.location = location
            return node

        side_on = texture_for(side_on_image, "Hair side-on capture", (0, 1900))
        numerator = side_on.outputs['Color']
        denominator = None

        def add_signal(socket, label, role, offset, default=0.0):
            """Add weight*socket into the running score, with the weight as its own 0..1 control."""
            nonlocal numerator, denominator
            weight_node, weight = HairOverlayService._bounded_factor(nodes, label, (340, offset), role, default)

            scaled = nodes.new('ShaderNodeMath')
            scaled.operation = 'MULTIPLY'
            scaled.location = (520, offset)
            links.new(socket, scaled.inputs[0])
            links.new(weight, scaled.inputs[1])

            summed = nodes.new('ShaderNodeMath')
            summed.operation = 'ADD'
            summed.location = (700, offset)
            links.new(numerator, summed.inputs[0])
            links.new(scaled.outputs['Value'], summed.inputs[1])
            numerator = summed.outputs['Value']

            # The divisor grows with the weights, so the score stays inside 0..1
            total = nodes.new('ShaderNodeMath')
            total.operation = 'ADD'
            total.location = (700, offset - 120)
            if denominator is None:
                total.inputs[0].default_value = 1.0
            else:
                links.new(denominator, total.inputs[0])
            links.new(weight, total.inputs[1])
            denominator = total.outputs['Value']
            return weight_node

        if images.get("root_tip") is not None:
            root_tip = texture_for(images["root_tip"], "Hair root/tip", (0, 1500))
            # Inverted so that low is bad, same as the side-on value
            towards_root = nodes.new('ShaderNodeMath')
            towards_root.operation = 'SUBTRACT'
            towards_root.location = (160, 1500)
            towards_root.inputs[0].default_value = 1.0
            links.new(root_tip.outputs['Color'], towards_root.inputs[1])
            add_signal(towards_root.outputs['Value'], "Also target the strand tips",
                       ROLE_SIDE_ON_TIPS, 1500, default=1.0)

        score = numerator
        if denominator is not None:
            normalised = nodes.new('ShaderNodeMath')
            normalised.operation = 'DIVIDE'
            normalised.location = (880, 1900)
            links.new(numerator, normalised.inputs[0])
            links.new(denominator, normalised.inputs[1])
            score = normalised.outputs['Value']

        # Not inert by default, these values work well for the volume shell (the only mode baking this map by default)
        _threshold_node, threshold = HairOverlayService._bounded_factor(
            nodes, "Hide hair caught end-on", (880, 1700), ROLE_SIDE_ON_CUTOFF, default=0.3)

        end_on = nodes.new('ShaderNodeMath')
        end_on.operation = 'LESS_THAN'
        end_on.label = "Below the threshold"
        end_on.location = (1060, 1900)
        links.new(score, end_on.inputs[0])
        links.new(threshold, end_on.inputs[1])

        keep = nodes.new('ShaderNodeMath')
        keep.operation = 'SUBTRACT'
        keep.label = "Keep the rest"
        keep.location = (1240, 1900)
        keep.inputs[0].default_value = 1.0
        links.new(end_on.outputs['Value'], keep.inputs[1])

        multiply = nodes.new('ShaderNodeMath')
        multiply.operation = 'MULTIPLY'
        multiply.label = "Alpha times side-on cutoff"
        multiply.location = (1420, 1780)
        links.new(alpha_socket, multiply.inputs[0])
        links.new(keep.outputs['Value'], multiply.inputs[1])
        return multiply.outputs['Value']

    @staticmethod
    def _multiply_in_depth_cutoff(node_tree: bpy.types.NodeTree, alpha_socket: bpy.types.NodeSocket, depth_image: bpy.types.Image) -> bpy.types.NodeSocket:
        """Hide texels whose hair was found too close to the surface. Returns the gated alpha socket.

        Undesired artifacts often appear where the shell sits on a strand, so the ray hits at almost no distance.
        With threshold 0 the comparison is false everywhere and the alpha is unchanged.
        """
        nodes = node_tree.nodes
        links = node_tree.links

        depth_texture = next((node for node in nodes
                              if node.bl_idname == 'ShaderNodeTexImage' and node.image == depth_image),
                             None)
        if depth_texture is None:
            return alpha_socket

        too_close = nodes.new('ShaderNodeMath')
        too_close.operation = 'LESS_THAN'
        too_close.label = "Hair closer than"
        too_close.location = (300, 1100)
        too_close.inputs[1].default_value = 0.0
        too_close[ROLE_TAG] = ROLE_DEPTH_CUTOFF
        links.new(depth_texture.outputs['Color'], too_close.inputs[0])

        keep = nodes.new('ShaderNodeMath')
        keep.operation = 'SUBTRACT'
        keep.label = "Keep the rest"
        keep.location = (480, 1100)
        keep.inputs[0].default_value = 1.0
        links.new(too_close.outputs['Value'], keep.inputs[1])

        multiply = nodes.new('ShaderNodeMath')
        multiply.operation = 'MULTIPLY'
        multiply.label = "Alpha times depth cutoff"
        multiply.location = (660, 980)
        links.new(alpha_socket, multiply.inputs[0])
        links.new(keep.outputs['Value'], multiply.inputs[1])
        return multiply.outputs['Value']

    @staticmethod
    def _multiply_in_edge_fade(node_tree: bpy.types.NodeTree, alpha_socket: bpy.types.NodeSocket, attribute_name: str) -> bpy.types.NodeSocket:
        """Attenuate an alpha socket at the shell rim by a per-vertex weight, and return the attenuated socket.

        Placed after the levels ramp, otherwise the ramp would make the faded rim opaque again.
        The To Min of the Map Range sets how transparent the rim gets.
        """
        nodes = node_tree.nodes
        links = node_tree.links

        attribute = nodes.new('ShaderNodeAttribute')
        attribute.attribute_type = 'GEOMETRY'
        attribute.attribute_name = attribute_name
        attribute.label = "Shell edge fade"
        attribute.location = (300, 620)

        strength = nodes.new('ShaderNodeMapRange')
        strength.label = "Edge fade strength"
        strength.location = (480, 620)
        strength.inputs['To Min'].default_value = 0.0
        strength.inputs['To Max'].default_value = 1.0
        links.new(attribute.outputs['Fac'], strength.inputs['Value'])

        multiply = nodes.new('ShaderNodeMath')
        multiply.operation = 'MULTIPLY'
        multiply.label = "Alpha times edge fade"
        multiply.location = (660, 500)
        multiply[ROLE_TAG] = ROLE_EDGE_FADE
        links.new(alpha_socket, multiply.inputs[0])
        links.new(strength.outputs['Result'], multiply.inputs[1])
        return multiply.outputs['Value']

    @staticmethod
    def _material_output(node_tree: bpy.types.NodeTree) -> bpy.types.Node | None:
        return next((n for n in node_tree.nodes if n.bl_idname == 'ShaderNodeOutputMaterial'), None)

    @staticmethod
    def apply_overlay(surface_obj: bpy.types.Object, asset_name: str, images: dict[str, bpy.types.Image]) -> int:
        """Blend the baked hair over the skin as a Mix Shader in front of the material output.

        Mixing shaders keeps the body opaque and the hair keeps its own roughness and normal.

        Returns how many material slots the overlay was applied to.
        """
        HairOverlayService.remove_overlay(surface_obj, asset_name)

        applied = 0
        for slot in surface_obj.material_slots:
            material = slot.material
            if material is None or not material.node_tree:
                continue
            node_tree = material.node_tree
            output = HairOverlayService._material_output(node_tree)
            if output is None or not output.inputs['Surface'].links:
                _LOG.warn("Skin material has no surface shader to blend over", material.name)
                continue

            skin_socket = output.inputs['Surface'].links[0].from_socket
            shader, alpha, created = HairOverlayService.build_fur_shader(node_tree, images, location=(-1400, -600))

            mix = node_tree.nodes.new('ShaderNodeMixShader')
            mix.location = (output.location[0] - 200, output.location[1] - 200)
            mix.label = "Fur overlay: " + asset_name
            node_tree.links.new(alpha, mix.inputs['Fac'])
            node_tree.links.new(skin_socket, mix.inputs[1])
            node_tree.links.new(shader, mix.inputs[2])
            node_tree.links.new(mix.outputs['Shader'], output.inputs['Surface'])

            for node in created + [mix]:
                node[OVERLAY_TAG] = asset_name
            applied += 1

        return applied

    @staticmethod
    def remove_overlay(surface_obj: bpy.types.Object | None, asset_name: str) -> int:
        """Take the overlay back out, reconnecting the skin shader from the first input of the Mix Shader."""
        if surface_obj is None:
            return 0
        removed = 0
        for slot in surface_obj.material_slots:
            material = slot.material
            if material is None or not material.node_tree:
                continue
            node_tree = material.node_tree
            tagged = [n for n in node_tree.nodes if n.get(OVERLAY_TAG) == asset_name]
            if not tagged:
                continue

            for mix in [n for n in tagged if n.bl_idname == 'ShaderNodeMixShader']:
                upstream = mix.inputs[1].links[0].from_socket if mix.inputs[1].links else None
                downstream = [link.to_socket for link in mix.outputs['Shader'].links]
                if upstream is not None:
                    for socket in downstream:
                        node_tree.links.new(upstream, socket)

            for node in tagged:
                node_tree.nodes.remove(node)
            removed += 1
        return removed

    @staticmethod
    def has_overlay(surface_obj: bpy.types.Object | None, asset_name: str) -> bool:
        """Whether this assets overlay is currently sitting in the surface material."""
        if surface_obj is None:
            return False
        for slot in surface_obj.material_slots:
            material = slot.material
            if material is None or not material.node_tree:
                continue
            if any(n.get(OVERLAY_TAG) == asset_name for n in material.node_tree.nodes):
                return True
        return False
