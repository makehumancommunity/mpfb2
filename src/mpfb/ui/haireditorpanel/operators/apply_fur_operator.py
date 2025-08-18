"""This module contains the Apply Fur Operator class."""

# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for loading fur assets, adding them to Human mesh and setting up UI for editing
# ------------------------------------------------------------------------------

from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
from ..hairproperties import FUR_PROPERTIES, DYNAMIC_FUR_PROPS_DEFINITIONS, DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS
import bpy, os

_LOG = LogService.get_logger("haireditorpanel.apply_fur_operator")

class MPFB_OT_ApplyFur_Operator(bpy.types.Operator):
    """Adds fur asset"""

    bl_idname = "mpfb.apply_fur_operator"
    bl_label = "Apply fur"
    bl_options = {'REGISTER'}

    hair_asset: bpy.props.StringProperty()

    def execute(self, context):

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'FINISHED'}

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)

        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'FINISHED'}

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        # Load hair asset
        blend_path = HairEditorService.get_fur_blend_path()
        object_name = self.hair_asset
        brace_name = f"{object_name}_brace"

        objects_to_load = []

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

            # Separate hair and brace
            hair_obj = next((obj for obj in data_to.objects if obj.name == object_name), None)
            brace_obj = next((obj for obj in data_to.objects if obj.name == brace_name), None)

            # Parent brace
            if brace_obj is not None:
                brace_obj.parent = basemesh
                brace_obj.matrix_parent_inverse = basemesh.matrix_world.inverted()


        except Exception as e:
            self.report({'ERROR'}, f"Failed to load fur object: {str(e)}")
            return {'CANCELLED'}


        # Activate hair object
        bpy.ops.object.select_all(action='DESELECT')
        hair_obj.select_set(True)
        context.view_layer.objects.active = hair_obj

        # Set Human as surface in Hair Curves data settings
        if hair_obj.type == 'CURVES':
            curves_data = hair_obj.data
            if hasattr(curves_data, 'surface'):
                curves_data.surface = basemesh
            else:
                self.report({'WARNING'}, "Curve object has no surface property")
        else:
            self.report({'WARNING'}, f"Object '{object_name}' is not curve!")

        # Parent hair to Human
        hair_obj.parent = basemesh
        hair_obj.matrix_parent_inverse = basemesh.matrix_world.inverted()

        # Define shape properties
        prop_prefix = f"{self.hair_asset}_"

        for name, (mod_name, attr, rng) in DYNAMIC_FUR_PROPS_DEFINITIONS.items():
            propname = f"{prop_prefix}{name}"
            propdef = {
                "name": propname,
                "type": "float",
                "description": mod_name,
                "max": rng[1],
                "min": rng[0],
                "default": hair_obj.modifiers[mod_name][attr]
                }
            FUR_PROPERTIES.set_value_dynamic(propname, hair_obj.modifiers[mod_name][attr], propdef, entity_reference=basemesh)

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

        # TODO: Port texture properties from the old version

        propname = f"{prop_prefix}fur_asset_open"
        propdef = {
            "name": propname,
            "type": "boolean",
            "label": f"{self.hair_asset}",
            "description": "Toggle visibility of fur properties",
            "default": False,
            "subtype": "panel_toggle"
            }

        FUR_PROPERTIES.set_value_dynamic(propname, False, propdef, entity_reference=basemesh)

        propname = f"{prop_prefix}fur_cards_are_generated"
        propdef = {
            "name": propname,
            "type": "boolean",
            "label": f"{self.hair_asset}",
            "description": "Toggle visibility of card placement and baking properties",
            "default": False,
            "subtype": "panel_toggle"
            }

        FUR_PROPERTIES.set_value_dynamic(propname, False, propdef, entity_reference=basemesh)

        propname = f"{prop_prefix}fur_cards_are_baked"
        propdef = {
            "name": propname,
            "type": "boolean",
            "label": f"{self.hair_asset}",
            "description": "Hides options for card placement and baking",
            "default": False,
            "subtype": "panel_toggle"
            }

        FUR_PROPERTIES.set_value_dynamic(propname, False, propdef, entity_reference=basemesh)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        self.report({'INFO'}, f"Applied new fur: {hair_obj.name}")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ApplyFur_Operator)
