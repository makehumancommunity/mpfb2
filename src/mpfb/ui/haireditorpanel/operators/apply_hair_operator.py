# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for loading hair assets, adding them to Human mesh and setting up UI for editing
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
from ..hairproperties import HAIR_PROPERTIES, DYNAMIC_HAIR_PROPS_DEFINITIONS, DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS
import bpy, os, json, shutil

_LOG = LogService.get_logger("haireditorpanel.apply_hair_operator")
_LOG.set_level(LogService.DEBUG)


class MPFB_OT_ApplyHair_Operator(bpy.types.Operator):
    """Adds hair asset"""
    bl_idname = "mpfb.apply_hair_operator"
    bl_label = "Apply hair"
    bl_options = {'REGISTER'}


    hair_asset: bpy.props.StringProperty()

    # Callback for editing hair asset geometry
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

    # Callback for editing material
    def make_material_callback(self, material_name, attribute_name, input_name):
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

            val = getattr(self, f"{material_name}_{attribute_name}")
            if hasattr(target_input, 'default_value'):
                target_input.default_value = val

        return callback

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

        scene = context.scene


        # Load hair asset
        blend_relative_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../data/hair/haireditor/hair.blend"))
        object_name = self.hair_asset
        brace_name = f"{object_name}_brace"

        objects_to_load = []
        brace_present = False

        try:
            with bpy.data.libraries.load(blend_relative_path, link=False) as (data_from, data_to):
                if object_name in data_from.objects:
                    objects_to_load.append(object_name)
                else:
                    self.report({'ERROR'}, f"Object '{object_name}' not found.")
                    return {'CANCELLED'}

                # Load eventual brace asset
                if brace_name in data_from.objects:
                    objects_to_load.append(brace_name)
                    brace_present = True

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

        for mod in basemesh.modifiers:
            _LOG.debug("Modifier", mod)

        for name, (mod_name, attr, rng) in DYNAMIC_HAIR_PROPS_DEFINITIONS.items():
            propname = f"{prop_prefix}{name}"
            propdef = {
                "name": propname,
                "type": "float",
                "description": mod_name,
                "max": rng[1],
                "min": rng[0],
                "default": hair_obj.modifiers[mod_name][attr]
                }
            HAIR_PROPERTIES.set_value_dynamic(propname, hair_obj.modifiers[mod_name][attr], propdef, entity_reference=basemesh)

        mat = hair_obj.active_material

        _LOG.debug("Material", mat)

        for name, definition in DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS.items():

            mod_name = definition[0]
            specification = definition[1]

            _LOG.debug("name, definition, modifier, specification", (name, definition, mod_name, specification))

            propname = f"{prop_prefix}{name}"
            propdef = {
                "name": propname,
                "description": mod_name,
                }

            if len(specification) > 2:
                # Assume this is a color
                pass
            else:
                # Assume this is a float
                minval = specification[0]
                maxval = specification[1]
                propdef["type"] = "float"
                propdef["min"] = minval
                propdef["max"] = maxval
                propdef["default"] = (minval + maxval) / 2.0
                HAIR_PROPERTIES.set_value_dynamic(propname, (minval + maxval) / 2, propdef, entity_reference=basemesh)

        propname = f"{prop_prefix}hair_asset_open"
        propdef = {
            "name": propname,
            "type": "boolean",
            "description": "Toggle visibility of hair properties",
            "default": False
            }

        HAIR_PROPERTIES.set_value_dynamic(propname, False, propdef, entity_reference=basemesh)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        for key in HAIR_PROPERTIES.get_keys(entity_reference=basemesh):
            _LOG.debug("Key", key)

        for item in basemesh.items():
            _LOG.debug("Item", item)

        self.report({'INFO'}, f"Applied new hair: {hair_obj.name}")
        return {'FINISHED'}

        mat = hair_obj.active_material
        if mat and mat.use_nodes:
            material_name = mat.name

            for name, (input_name, rng) in material_props.items():
                prop_id = f"{material_name}_{name}"
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
                            update=self.make_material_callback(material_name, name, input_name)
                        )
                    else:
                        prop = bpy.props.FloatProperty(
                            name=name.replace("_", " ").capitalize(),
                            min=rng[0],
                            max=rng[1],
                            default=(rng[0] + rng[1]) / 2,
                            update=self.make_material_callback(material_name, name, input_name)
                        )

                    setattr(scene.__class__, prop_id, prop)

        # Property for UI drawer
        prop_id = f"{prop_prefix}hair_asset_open"
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

        scene.hair_setup = True

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ApplyHair_Operator)