"""This module contains the Apply Fur Operator class."""

# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025 - updated 6.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for loading fur assets, adding them to Human mesh and setting up UI for editing
# ------------------------------------------------------------------------------

from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
from ....services.modifierservice import ModifierService
from ...mpfboperator import MpfbOperator
from ...pollstrategy import pollstrategy, PollStrategy
from ..hairproperties import FUR_PROPERTIES, DYNAMIC_FUR_PROPS_DEFINITIONS, DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS, \
    set_cards_flag, PACK_NAME_PROPERTY, create_cards_config_properties, create_cards_bake_properties
from ..hairsetup import ensure_hair_setup
import bpy, os
from mathutils import Matrix

_LOG = LogService.get_logger("haireditorpanel.apply_fur_operator")

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_ApplyFur_Operator(MpfbOperator):
    """Adds fur asset"""

    bl_idname = "mpfb.apply_fur_operator"
    bl_label = "Apply fur"
    bl_options = {'REGISTER', 'UNDO'}

    hair_asset: bpy.props.StringProperty()

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'CANCELLED'}

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)

        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'CANCELLED'}

        # The character has to be prepared for hair editing
        ensure_hair_setup(basemesh, context)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        # Load hair asset
        blend_path = HairEditorService.get_fur_blend_path()
        object_name = self.hair_asset
        brace_name = f"{object_name}_brace"

        objects_to_load = []
        images_before_load = HairEditorService.list_image_names()

        try:
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                if object_name in data_from.objects:
                    objects_to_load.append(object_name)
                else:
                    self.report({'ERROR'}, f"Object '{object_name}' not found.")
                    return {'CANCELLED'}

                # Load eventual brace asset
                if brace_name in data_from.objects:
                    objects_to_load.append(brace_name)

                data_to.objects = objects_to_load

            # Link objects to the scene
            for obj in data_to.objects:
                if obj is not None:
                    bpy.context.collection.objects.link(obj)

            # data_to.objects keeps the same order as objects_to_load
            hair_obj = data_to.objects[0]
            brace_obj = data_to.objects[1] if len(objects_to_load) > 1 else None

        except Exception as e:
            self.report({'ERROR'}, f"Failed to load fur object: {str(e)}")
            return {'CANCELLED'}

        asset_name = hair_obj.name
        hair_obj[PACK_NAME_PROPERTY] = object_name

        # Parent brace, renamed to ensure corresponding with the hair object it belongs to
        if brace_obj is not None:
            brace_obj.name = f"{asset_name}_brace"
            brace_obj[PACK_NAME_PROPERTY] = object_name
            brace_obj.parent = basemesh
            brace_obj.matrix_parent_inverse = Matrix.Identity(4)

        # Activate hair object
        bpy.ops.object.select_all(action='DESELECT')
        hair_obj.select_set(True)
        context.view_layer.objects.active = hair_obj

        # Set Human as surface in Hair Curves data settings
        if not HairEditorService.attach_curves_to_basemesh(hair_obj, basemesh):
            self.report({'WARNING'}, f"Object '{object_name}' is not hair curves!")

        HairEditorService.discard_unused_images(images_before_load)

        # Parent hair to Human. The asset was groomed on a character standing at the origin.
        # Own transform is therefore relative to that character and has to stay so - an identity parent
        # inverse puts it on this character wherever it stands.
        hair_obj.parent = basemesh
        hair_obj.matrix_parent_inverse = Matrix.Identity(4)

        # Define shape properties
        prop_prefix = f"{asset_name}_"

        for name, (mod_name, attr, rng) in DYNAMIC_FUR_PROPS_DEFINITIONS.items():
            propname = f"{prop_prefix}{name}"
            propdef = {
                "name": propname,
                "type": "float",
                "description": mod_name,
                "max": rng[1],
                "min": rng[0],
                "default": ModifierService.get_node_group_input(hair_obj.modifiers[mod_name], attr)
                }
            FUR_PROPERTIES.set_value_dynamic(propname, ModifierService.get_node_group_input(hair_obj.modifiers[mod_name], attr), propdef, entity_reference=basemesh)

        mat = hair_obj.active_material

        _LOG.debug("Material", mat)

        for name, definition in DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS.items():

            mod_name = definition[0]
            specification = definition[1]

            _LOG.debug("name, definition, modifier, specification", (name, definition, mod_name, specification))

            propname = f"{prop_prefix}{name}"
            propdef = {
                "name": propname,
                "description": mod_name,
                }

            if type(specification) == bool:
                propdef["type"] = "boolean"
                propdef["default"] = specification
                FUR_PROPERTIES.set_value_dynamic(propname, specification, propdef, entity_reference=basemesh)

            elif type(specification) == str:
                propdef["type"] = "path"
                propdef["default"] = specification
                FUR_PROPERTIES.set_value_dynamic(propname, specification, propdef, entity_reference=basemesh)

            elif len(specification) > 2:
                propdef["type"] = "color"
                propdef["default"] = list(specification) # To make a clone
                FUR_PROPERTIES.set_value_dynamic(propname, list(specification), propdef, entity_reference=basemesh)
            else:
                # Assume this is a float
                minval = specification[0]
                maxval = specification[1]
                propdef["type"] = "float"
                propdef["min"] = minval
                propdef["max"] = maxval
                propdef["default"] = (minval + maxval) / 2.0
                FUR_PROPERTIES.set_value_dynamic(propname, (minval + maxval) / 2, propdef, entity_reference=basemesh)

        propname = f"{prop_prefix}fur_asset_open"
        propdef = {
            "name": propname,
            "type": "boolean",
            "label": asset_name,
            "description": "Toggle visibility of fur properties",
            "default": False,
            "subtype": "panel_toggle"
            }

        FUR_PROPERTIES.set_value_dynamic(propname, False, propdef, entity_reference=basemesh)

        # Creating card generation and baking properties upfront
        create_cards_config_properties(FUR_PROPERTIES, basemesh, asset_name)
        create_cards_bake_properties(FUR_PROPERTIES, basemesh, asset_name)

        set_cards_flag(FUR_PROPERTIES, basemesh, asset_name, "fur", "generated", False)
        set_cards_flag(FUR_PROPERTIES, basemesh, asset_name, "fur", "baked", False)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        self.report({'INFO'}, f"Applied new fur: {hair_obj.name}")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ApplyFur_Operator)
