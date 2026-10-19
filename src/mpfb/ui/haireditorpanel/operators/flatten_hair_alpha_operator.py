# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         22.9.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for writing the tuned alpha back into the colour texture
# ------------------------------------------------------------------------------
"""Write the result of the alpha controls (levels ramp and cutoffs) into the colour texture alpha channel and remove the controls.

The alpha is evaluated by baking it with cycles. This cannot be undone - unbake and bake again to start over.
"""

from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from ....services.haireditorservices import HairEditorService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ...pollstrategy import pollstrategy, PollStrategy
from ..hairproperties import (HAIR_PROPERTIES, FUR_PROPERTIES, CARDS_OBJECT_SUFFIX,
                              BAKED_EXTRA_MAP_KEYS, get_cards_flag, get_bake_target,
                              resolve_custom_surface)
from ....services import haircardservice as cg
from ....services.hairoverlayservice import HairOverlayService

import bpy

_LOG = LogService.get_logger("haireditorpanel.flatten_hair_alpha_operator")

# Maps which only drive the alpha, they would apply the tuning a second time if left in the material
_ALPHA_ONLY_MAPS = ("side_on", "depth")


def alpha_source_socket(node_tree):
    """The socket feeding the Principled shaders Alpha, or None if nothing does."""
    if node_tree is None:
        return None
    principled = next((node for node in node_tree.nodes
                       if node.bl_idname == 'ShaderNodeBsdfPrincipled'), None)
    if principled is None:
        return None
    wanted = principled.inputs['Alpha']
    for link in node_tree.links:
        if (link.to_node.as_pointer() == principled.as_pointer()
                and link.to_socket.identifier == wanted.identifier):
            return link.from_socket
    return None


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_FlattenHairAlpha_Operator(MpfbOperator):
    """Write the tuned alpha into the colour texture and remove the controls that produced it"""

    bl_idname = "mpfb.flatten_hair_alpha_operator"
    bl_label = "Bake alpha into the texture"
    bl_options = {'REGISTER'}

    hair_asset: bpy.props.StringProperty()
    is_fur: bpy.props.BoolProperty(default=False)

    def get_logger(self):
        return _LOG

    def _target_object(self, basemesh, properties):
        """The object carrying the baked material, whichever target was used."""
        target = get_bake_target(properties, basemesh, self.hair_asset)
        if target == cg.BAKE_TARGET_CUSTOM:
            return resolve_custom_surface(properties, basemesh, self.hair_asset)
        return bpy.data.objects.get(self.hair_asset + CARDS_OBJECT_SUFFIX)

    def _bake_alpha(self, context, obj, material, resolution):
        """EMIT-bake whatever feeds the Principled's alpha. Returns a flat numpy array or None."""
        import numpy as np

        alpha = alpha_source_socket(material.node_tree)
        if alpha is None:
            self.report({'ERROR'}, "Nothing is driving the alpha, so there is nothing to write")
            return None

        scene = context.scene
        before = {
            "engine": scene.render.engine,
            "samples": getattr(scene.cycles, "samples", None),
            "direct": scene.render.bake.use_pass_direct,
            "indirect": scene.render.bake.use_pass_indirect,
            "clear": scene.render.bake.use_clear,
            "selected_to_active": scene.render.bake.use_selected_to_active,
        }
        probe = material.copy()
        image = bpy.data.images.new(f"{self.hair_asset}_alpha_flatten", resolution, resolution,
                                    alpha=False, float_buffer=False)
        image.colorspace_settings.name = 'Non-Color'
        original_materials = [slot.material for slot in obj.material_slots]
        try:
            # The copy is rewired, so the original material stays untouched
            tree = probe.node_tree
            output = next((node for node in tree.nodes
                           if node.bl_idname == 'ShaderNodeOutputMaterial'), None)
            emission = tree.nodes.new('ShaderNodeEmission')
            emission.location = (output.location.x, output.location.y - 300) if output else (0, 0)
            source = alpha_source_socket(tree)
            if source is None or output is None:
                self.report({'ERROR'}, "Could not rewire the material to read its alpha back")
                return None
            tree.links.new(source, emission.inputs['Color'])
            tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

            target = tree.nodes.new('ShaderNodeTexImage')
            target.image = image
            tree.nodes.active = target

            obj.data.materials.clear()
            obj.data.materials.append(probe)

            scene.render.engine = 'CYCLES'
            if hasattr(scene.cycles, "samples"):
                scene.cycles.samples = 1
            scene.render.bake.use_pass_direct = False
            scene.render.bake.use_pass_indirect = False
            scene.render.bake.use_clear = True
            scene.render.bake.use_selected_to_active = False

            ObjectService.deselect_and_deactivate_all()
            ObjectService.activate_blender_object(obj)
            bpy.ops.object.bake(type='EMIT')

            return np.clip(
                HairEditorService.read_image_pixels(image).reshape(-1, 4)[:, :3].max(axis=1),
                0.0, 1.0)
        finally:
            obj.data.materials.clear()
            for slot_material in original_materials:
                obj.data.materials.append(slot_material)
            bpy.data.materials.remove(probe, do_unlink=True)
            bpy.data.images.remove(image, do_unlink=True)
            scene.render.engine = before["engine"]
            if before["samples"] is not None:
                scene.cycles.samples = before["samples"]
            scene.render.bake.use_pass_direct = before["direct"]
            scene.render.bake.use_pass_indirect = before["indirect"]
            scene.render.bake.use_clear = before["clear"]
            scene.render.bake.use_selected_to_active = before["selected_to_active"]

    def hardened_execute(self, context):
        _LOG.enter()
        import numpy as np

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'CANCELLED'}

        properties = FUR_PROPERTIES if self.is_fur else HAIR_PROPERTIES
        kind = "fur" if self.is_fur else "hair"
        if not get_cards_flag(properties, basemesh, self.hair_asset, kind, "baked"):
            self.report({'ERROR'}, "There is nothing baked to write the alpha into")
            return {'CANCELLED'}

        obj = self._target_object(basemesh, properties)
        if obj is None or not obj.data.materials or obj.data.materials[0] is None:
            self.report({'ERROR'}, "Could not find the baked object and its material")
            return {'CANCELLED'}
        material = obj.data.materials[0]

        colour = bpy.data.images.get(f"{self.hair_asset}_cards_texture")
        if colour is None:
            self.report({'ERROR'}, "The baked colour texture is not in the file any more")
            return {'CANCELLED'}
        width, height = colour.size
        if width != height:
            self.report({'ERROR'}, f"Expected a square texture, got {width}x{height}")
            return {'CANCELLED'}

        flattened = self._bake_alpha(context, obj, material, width)
        if flattened is None:
            return {'CANCELLED'}

        pixels = HairEditorService.read_image_pixels(colour).reshape(-1, 4)
        if len(flattened) != len(pixels):
            self.report({'ERROR'}, "The alpha came back a different size than the colour texture")
            return {'CANCELLED'}
        before = float((pixels[:, 3] > 0.5).mean())
        pixels[:, 3] = flattened
        HairEditorService.write_image_pixels(colour, pixels)
        after = float((pixels[:, 3] > 0.5).mean())

        if colour.filepath_raw:
            colour.save()

        # Rebuilt without the maps that only fed the alpha, so the tuning is not applied twice
        images = {key: image for key, image in self._baked_images(material).items()
                  if key not in _ALPHA_ONLY_MAPS}
        images["color"] = colour
        rebuilt = HairOverlayService.build_baked_material(f"{self.hair_asset}_baked_flat", images)
        obj.data.materials.clear()
        obj.data.materials.append(rebuilt)
        if material.users == 0:
            bpy.data.materials.remove(material, do_unlink=True)

        dropped = [key for key in _ALPHA_ONLY_MAPS
                   if bpy.data.images.get(f"{self.hair_asset}_cards_{key}") is not None]
        message = (f"Alpha written into {colour.name} "
                   f"({before * 100:.1f}% opaque before, {after * 100:.1f}% after)")
        if dropped:
            message += f"; {', '.join(dropped)} no longer needed for export"
        self.report({'INFO'}, message)
        return {'FINISHED'}

    def _baked_images(self, material):
        """The baked maps this material is using, keyed the way build_baked_material wants them."""
        names = {"color": f"{self.hair_asset}_cards_texture"}
        for key in BAKED_EXTRA_MAP_KEYS:
            names[key] = f"{self.hair_asset}_cards_{key}"

        sampled = {node.image.as_pointer() for node in material.node_tree.nodes
                   if node.bl_idname == 'ShaderNodeTexImage' and node.image is not None}
        found = {}
        for key, name in names.items():
            image = bpy.data.images.get(name)
            if image is not None and image.as_pointer() in sampled:
                found[key] = image
        return found


ClassManager.add_class(MPFB_OT_FlattenHairAlpha_Operator)
