# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.9.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for putting a baked fur overlay back into a regenerated skin material
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ...pollstrategy import pollstrategy, PollStrategy
from ..hairproperties import (HAIR_PROPERTIES, FUR_PROPERTIES, baked_image_names,
                              get_cards_flag, resolve_body_surface, body_has_material)
from ....services.hairoverlayservice import HairOverlayService
from ....services.hairbakeservice import HairBakeService

import bpy, os

_LOG = LogService.get_logger("haireditorpanel.reapply_overlay_operator")


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_ReapplyFurOverlay_Operator(MpfbOperator):
    """Puts a baked hair (Body texture mode) result back into the skin material, for example after the skin was changed. No rebake needed."""
    bl_idname = "mpfb.reapply_fur_overlay_operator"
    bl_label = "Reapply overlay"
    bl_options = {'REGISTER', 'UNDO'}

    hair_asset: bpy.props.StringProperty()
    is_fur: bpy.props.BoolProperty(default=False)

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'CANCELLED'}

        properties = FUR_PROPERTIES if self.is_fur else HAIR_PROPERTIES
        kind = "fur" if self.is_fur else "hair"

        if not get_cards_flag(properties, basemesh, self.hair_asset, kind, "baked"):
            self.report({'ERROR'}, "There is no baked result for this asset to reapply")
            return {'CANCELLED'}

        surface_obj = resolve_body_surface(basemesh)
        if not body_has_material(surface_obj):
            self.report({'ERROR'}, f"'{surface_obj.name}' has no skin material to blend the hair over")
            return {'CANCELLED'}

        destination = properties.get_value(f"{self.hair_asset}_cards_texture_dst", "", entity_reference=basemesh)
        images = self._collect_images(destination)
        if images.get("color") is None:
            self.report({'ERROR'},
                        "Could not find the baked colour texture, in the file or on disk; bake again")
            return {'CANCELLED'}

        applied = HairOverlayService.apply_overlay(surface_obj, self.hair_asset, images)
        if not applied:
            self.report({'ERROR'}, "No skin material could be found to blend the hair over")
            return {'CANCELLED'}

        self.report({'INFO'},
                    f"Reapplied the '{self.hair_asset}' overlay to {applied} material slot(s) "
                    f"of '{surface_obj.name}'")
        return {'FINISHED'}

    def _collect_images(self, destination):
        """The baked maps, preferring the datablocks still in the file and falling back to disk."""
        images = {}
        for name in baked_image_names(self.hair_asset):
            # "<asset>_cards_texture" is the colour map, the rest are "<asset>_cards_<key>"
            key = "color" if name.endswith("_cards_texture") else name.rsplit("_cards_", 1)[-1]
            image = bpy.data.images.get(name)
            if image is None:
                suffix = "" if key == "color" else f"_{key}"
                path = HairBakeService.resolve_bake_path(self.hair_asset, destination, suffix=suffix)
                if os.path.isfile(path):
                    try:
                        image = bpy.data.images.load(path, check_existing=True)
                        image.name = name
                        image.colorspace_settings.name = 'sRGB' if key == "color" else 'Non-Color'
                        if key != "color":
                            image.use_fake_user = True
                    except Exception as e:
                        _LOG.warn("Could not load a baked map back from disk", (path, e))
                        image = None
            if image is not None:
                images[key] = image
        return images

ClassManager.add_class(MPFB_OT_ReapplyFurOverlay_Operator)
