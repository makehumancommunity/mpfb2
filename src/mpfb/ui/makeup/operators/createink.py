"""Operator for adding an empty ink layer to a material."""

import bpy, os, json, gzip
from ....services import LocationService
from ....services import LogService
from ....services import ObjectService
from ....services import MaterialService
from ....services import MeshService
from ....entities.material.makeskinmaterial import MakeSkinMaterial
from ..makeuppanel import MAKEUP_PROPERTIES

from .... import ClassManager

_LOG = LogService.get_logger("makeup.createink")


class MPFB_OT_CreateInkOperator(bpy.types.Operator):
    """Add a new empty ink layer to the mesh's existing material. Only MakeSkin materials are supported."""

    bl_idname = "mpfb.create_ink"
    bl_label = "Create ink"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Check if the operator can run in the current context and that a mesh object is active."""
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        """Create a new empty ink layer on the selected object, optionally importing a specific UV map."""
        mesh_object = context.active_object

        # Ensure the active object is a basemesh
        if not ObjectService.object_is_basemesh(mesh_object):
            self.report({'ERROR'}, "The active object is not a basemesh.")
            return {'CANCELLED'}

        # Use MaterialService to check that the mesh object has a MakeSkin material
        if not MaterialService.has_materials(mesh_object):
            self.report({'ERROR'}, "The mesh object does not have any materials.")
            return {'CANCELLED'}

        material = MaterialService.get_material(mesh_object)
        if MaterialService.identify_material(material) != "makeskin":
            self.report({'ERROR'}, "Only MakeSkin materials are supported.")
            return {'CANCELLED'}

        makeskin = MakeSkinMaterial()
        makeskin.populate_from_object(mesh_object)
        makeskin.ensure_uvmap_node_for_texture_nodes(mesh_object)

        focus_name = MAKEUP_PROPERTIES.get_value("focus_name", entity_reference=context.scene)
        create_ink = MAKEUP_PROPERTIES.get_value("create_ink", entity_reference=context.scene)
        resolution = MAKEUP_PROPERTIES.get_value("resolution", entity_reference=context.scene)

        if not focus_name:
            self.report({'ERROR'}, "A focus name must be chosen.")
            return {'CANCELLED'}

        if focus_name != "NONE":
            _LOG.debug("Adding focus:", focus_name)

            # focus_filename is the absolute path to the json file containing serialized UV map
            focus_filename = os.path.join(LocationService.get_user_data("uv_layers"), focus_name)
            if not os.path.exists(focus_filename):
                focus_filename = os.path.join(LocationService.get_mpfb_data("uv_layers"), focus_name)

            focus_name = str(focus_name).replace(".gz", "").replace(".json", "").replace("_", " ")

            # Load the UV map from the JSON file
            try:
                _LOG.debug("Loading UV map from file:", focus_filename)
                if focus_filename.endswith(".gz"):
                    with gzip.open(focus_filename, 'rt') as f:
                        uv_map_as_dict = json.load(f)
                else:
                    with open(focus_filename, 'r') as f:
                        uv_map_as_dict = json.load(f)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to load UV map from file: {e}")
                return {'CANCELLED'}

            # Add the UV map to the active object
            try:
                MeshService.add_uv_map_from_dict(mesh_object, focus_name, uv_map_as_dict)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to add UV map to mesh: {e}")
                return {'CANCELLED'}

            # Set the new UV map as active
            uv_map = mesh_object.data.uv_layers.get(focus_name)
            if uv_map:
                _LOG.debug("Setting UV map as active.", focus_name)
                mesh_object.data.uv_layers.active = uv_map
                mesh_object.data.uv_layers[focus_name].active_render = True
            else:
                self.report({'ERROR'}, f"Failed to set UV map '{focus_name}' as active.")
                return {'CANCELLED'}
        else:
            focus_name = mesh_object.data.uv_layers[0].name

        # Add an ink layer to the material, get the relevant new nodes
        uvmap_node, texture_node, ink_layer_id = MaterialService.add_focus_nodes(material, uv_map_name=focus_name)

        if create_ink:
            # Create a new image instance and add it to the texture_node
            res = int(resolution)
            image = bpy.data.images.new(name="inkLayer" + str(ink_layer_id), width=res, height=res, alpha=True)
            image.generated_color = (1.0, 1.0, 1.0, 0.0)
            texture_node.image = image

        self.report({'INFO'}, f"Ink layer 'inkLayer{ink_layer_id}' added. Make sure to select it in the texture paint editor before painting.")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateInkOperator)
