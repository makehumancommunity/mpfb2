# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for loading card asset or generating it
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.locationservice import LocationService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
import bpy, os, json, shutil, bpy_extras
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
from mathutils import Vector
import bmesh
import tempfile

_LOG = LogService.get_logger("haireditorpanel.generate_hair_cards_operator")


class MPFB_OT_GenerateHairCards_Operator(bpy.types.Operator):
    """Converts curve based hair to card object"""
    bl_idname = "mpfb.generate_hair_cards_operator"
    bl_label = "Generate hair cards"
    bl_options = {'REGISTER'}


    hair_asset: bpy.props.StringProperty()
    card_asset: bpy.props.StringProperty()

    # Callback to modify generating of cards through UI
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


    def execute(self, context):

        scene = context.scene

        # Get default export destination
        actual_dir = os.path.dirname(__file__)
        default_dir = os.path.join(actual_dir, "../../../data/user_export/")

        # Get Human mesh
        human_obj = context.object
        if (not human_obj or not human_obj.name == 'Human'):
            self.report({'ERROR'}, "Object Human must be active")
            return {'CANCELLED'}

        # Get hair asset
        hair_obj = None
        for child in human_obj.children:
            if child.name == self.hair_asset:
                hair_obj = child
                break
        if not hair_obj:
            self.report({'WARNING'}, f"Hair object '{self.hair_asset}' not found")
            return {'CANCELLED'}

        # Try to load card asset from hair asset file
        blend_relative_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../data/hair/haireditor/{self.hair_asset}.blend"))
        object_name = f"{self.hair_asset}_cards"
        cards_loaded = False

        objects_to_load = []
        try:
            with bpy.data.libraries.load(blend_relative_path, link=False) as (data_from, data_to):
                if object_name in data_from.objects:
                    objects_to_load.append(object_name)

                data_to.objects = objects_to_load

            card_obj = data_to.objects[0]
            if card_obj is not None:
                bpy.context.collection.objects.link(card_obj)

                # Allign card asset aproximately to the object asset
                bb_world = [hair_obj.matrix_world @ Vector(corner) for corner in hair_obj.bound_box]
                center = sum(bb_world, Vector()) / len(bb_world)
                card_obj.location = center

                card_obj.parent = human_obj
                card_obj.matrix_parent_inverse = human_obj.matrix_world.inverted()

                self.report({'INFO'}, f"'{self.hair_asset}' successfully imported. You might need to manualy align it to fit correctly.")

                cards_loaded = True


        except Exception as e:
            self.report({'INFO'}, f"No cards to load, generating new.")

        # Generate hair cards
        if(not cards_loaded):
            # Duplicate hair asset to create base for card asset
            card_obj = hair_obj.copy()
            card_obj.data = hair_obj.data.copy()
            card_obj.name = self.card_asset
            context.collection.objects.link(card_obj)

            # Setup geo nodes
            geo_mod = card_obj.modifiers.new(name="HairCards", type='NODES')
            node_group = bpy.data.node_groups.new(card_obj.name + "_HairCards", 'GeometryNodeTree')
            geo_mod.node_group = node_group

            iface = node_group.interface
            iface.new_socket('Geometry', in_out='INPUT',  socket_type='NodeSocketGeometry')
            iface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

            # Create nodes
            nodes = node_group.nodes
            links = node_group.links

            # Clear default nodes
            for n in nodes:
                nodes.remove(n)

            # Input output
            group_in  = nodes.new('NodeGroupInput')
            group_out = nodes.new('NodeGroupOutput')
            group_in.location  = (-600, 0)
            group_out.location = ( 600, 0)

            # Resample curve
            resample = nodes.new('GeometryNodeResampleCurve')
            resample.mode      = 'COUNT'
            resample.inputs['Count'].default_value = 10
            resample.location  = (-300, 200)

            # Grid as base for card
            grid = nodes.new('GeometryNodeMeshGrid')
            grid.inputs['Size X'].default_value = 0.3
            grid.inputs['Size Y'].default_value = 0.3
            grid.inputs['Vertices X'].default_value = 3
            grid.inputs['Vertices Y'].default_value = 3
            grid.location   = (-300, -200)

            # Instance on points
            inst = nodes.new('GeometryNodeInstanceOnPoints')
            inst.location = (0, 0)

            # Vector rotate
            vec_rot = nodes.new("ShaderNodeVectorRotate")
            vec_rot.rotation_type = 'AXIS_ANGLE'
            vec_rot.inputs['Angle'].default_value = 1.57
            vec_rot.inputs[1].default_value[1]=1
            vec_rot.location = (50, 100)

            # Curve tangent (for card rotation)
            tangent_node = nodes.new('GeometryNodeInputTangent')
            tangent_node.location = (-50, 250)



            # Link tangent to vector and axis
            links.new(tangent_node.outputs['Tangent'], vec_rot.inputs['Vector'])
            links.new(tangent_node.outputs['Tangent'], vec_rot.inputs['Axis'])
            links.new(vec_rot.outputs['Vector'], inst.inputs['Rotation'])

            # Scale
            scale = nodes.new('GeometryNodeScaleElements')
            scale.inputs['Scale'].default_value = 0.2
            scale.location = (350, 0)

            # Realize instances
            real = nodes.new('GeometryNodeRealizeInstances')
            real.location = (450, 0)

            # Random value as input for Greater than
            rand = nodes.new('FunctionNodeRandomValue')
            rand.data_type = 'FLOAT'
            rand.location = (150, -200)

            # Greater than for density moderation
            greater = nodes.new('FunctionNodeCompare')
            greater.operation = 'GREATER_THAN'
            greater.inputs[1].default_value = 0.001
            greater.location = (350, -200)

            # Delete geometry based on 2 previous nodes
            delete = nodes.new('GeometryNodeDeleteGeometry')
            delete.domain    = 'FACE'
            delete.location  = (550, -100)

            # Add inputs for UI editing
            scale_socket = iface.new_socket('Scale', in_out='INPUT', socket_type='NodeSocketFloat')
            scale_socket.default_value = 0.2
            scale_socket.min_value = 0.0
            scale_socket.max_value = 1.0

            density_socket = iface.new_socket('Density', in_out='INPUT', socket_type='NodeSocketFloat')
            density_socket.default_value = 0.001
            density_socket.min_value = 0.0
            density_socket.max_value = 1.0

            shape_socket = iface.new_socket('Shape', in_out='INPUT', socket_type='NodeSocketFloat')
            shape_socket.default_value = 1.0
            shape_socket.min_value = 0.0
            shape_socket.max_value = 1000.0

            # Link everything up
            links.new(group_in.outputs['Geometry'], resample.inputs['Curve'])
            links.new(resample.outputs['Curve'], inst.inputs['Points'])
            links.new(grid.outputs['Mesh'], inst.inputs['Instance'])
            links.new(inst.outputs['Instances'], scale.inputs['Geometry'])
            links.new(scale.outputs['Geometry'], real.inputs['Geometry'])
            links.new(real.outputs['Geometry'], delete.inputs['Geometry'])
            links.new(rand.outputs['Value'], greater.inputs[0])
            links.new(greater.outputs['Result'], delete.inputs['Selection'])
            links.new(delete.outputs['Geometry'], group_out.inputs['Geometry'])
            links.new(group_in.outputs['Scale'], scale.inputs['Scale'])
            links.new(group_in.outputs['Density'], greater.inputs[1])
            links.new(group_in.outputs['Shape'], rand.inputs['Seed'])
            # TODO: maybe place along huma normals + random offset with slider in ui/add option to create own card asset


            # Define card generation properties
            prop_prefix = f"{self.card_asset}_"

            props = {
                "scale": ("HairCards", "Socket_2", (0.0, 1.0), 0.2),
                "density": ("HairCards", "Socket_3", (0.0, 0.01), 0.001),
                "placement": ("HairCards", "Socket_4", (0.0, 1000.0), 1)
            }


            #TODO: Placement should be int...
            for name, (mod_name, attr, rng, default) in props.items():
                prop_id = f"{prop_prefix}{name}"
                if not hasattr(scene.__class__, prop_id):
                    setattr(
                        scene.__class__,
                        prop_id,
                        bpy.props.FloatProperty(
                            name=name.replace("_", " ").capitalize(),
                            default=default,
                            min = rng[0],
                            max =rng[1],
                            update=self.make_update_callback(card_obj,mod_name, attr,name, rng)
                        )
                    )
            # Force default vals
            try:
                geo_mod["Socket_2"] = 0.2
                geo_mod["Socket_3"] = 0.001
                geo_mod["Socket_4"] = 1
            except KeyError:
                self.report({'WARNING'}, "Modifier inputs not found to set default values.")


        # Property to update UI
        prop_id = f"{self.card_asset}_generated"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.BoolProperty(
                name=prop_id,
                description=f"Card asset generated.",
                default=True
                )
            )
        if hasattr(scene, prop_id):
            setattr(scene, prop_id, True)

        # Properties for further baking
        prop_id = f"{self.card_asset}_samples"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.IntProperty(
                name=prop_id,
                description=f"Render samples for card baking",
                default=32
                )
            )
        prop_id = f"{self.card_asset}_resolution"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.IntProperty(
                name=prop_id,
                description=f"Resolution of baked card texture",
                default=1024
                )
            )
        prop_id = f"{self.card_asset}_glossy"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.BoolProperty(
                name=prop_id,
                description=f"Bake as glossy or diffuse?",
                default=True
                )
            )
        prop_id = f"{self.card_asset}_texture_dst"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.StringProperty(
                    name=prop_id,
                    description="Directory to save baked texture",
                    subtype='DIR_PATH',
                    default=default_dir
                )
            )

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_GenerateHairCards_Operator)