"""Operator for adding an empty ink layer to a material."""

import bpy, os, json, gzip
from .....services import LocationService
from .....services import LogService
from .....services import ObjectService
from .....services import MaterialService
from .....services import MeshService
from .....entities.material.makeskinmaterial import MakeSkinMaterial
from ..makeuppanel import MAKEUP_PROPERTIES

from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("makeup.createink")


@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_CreateInkOperator(MpfbOperator):
    """Add a new empty ink layer to the mesh's existing material. Only MakeSkin materials are supported."""

    bl_idname = "mpfb.create_ink"
    bl_label = "Create ink"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        """Create a new empty ink layer on the selected object, optionally importing a specific UV map."""
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=MAKEUP_PROPERTIES)

        # Ensure the active object is a basemesh
        if not ObjectService.object_is_basemesh(ctx.active_object):
            self.report({'ERROR'}, "The active object is not a basemesh.")
            return {'CANCELLED'}

        # Use MaterialService to check that the mesh object has a MakeSkin material
        if not MaterialService.has_materials(ctx.active_object):
            self.report({'ERROR'}, "The mesh object does not have any materials.")
            return {'CANCELLED'}

        material = MaterialService.get_material(ctx.active_object)
        if MaterialService.identify_material(material) != "makeskin":
            self.report({'ERROR'}, "Only MakeSkin materials are supported.")
            return {'CANCELLED'}

        makeskin = MakeSkinMaterial()
        makeskin.populate_from_object(ctx.active_object)
        makeskin.ensure_uvmap_node_for_texture_nodes(ctx.active_object)

        if not ctx.focus_name:
            self.report({'ERROR'}, "A focus name must be chosen.")
            return {'CANCELLED'}

        if ctx.focus_name != "NONE":
            _LOG.debug("Adding focus:", ctx.focus_name)

            # focus_filename is the absolute path to the json file containing serialized UV map
            focus_filename = os.path.join(LocationService.get_user_data("uv_layers"), ctx.focus_name)
            if not os.path.exists(focus_filename):
                focus_filename = os.path.join(LocationService.get_mpfb_data("uv_layers"), ctx.focus_name)

            focus_name = str(ctx.focus_name).replace(".gz", "").replace(".json", "").replace("_", " ")

            # Load the UV map from the JSON file
            try:
                _LOG.debug("Loading UV map from file:", focus_filename)
                if focus_filename.endswith(".gz"):
                    with gzip.open(focus_filename, 'rt') as json_file:
                        uv_map_as_dict = json.load(json_file)
                else:
                    with open(focus_filename, 'r', encoding="utf-8") as json_file:
                        uv_map_as_dict = json.load(json_file)
            except Exception as excp:
                self.report({'ERROR'}, f"Failed to load UV map from file: {excp}")
                return {'CANCELLED'}

            # Add the UV map to the active object
            try:
                MeshService.add_uv_map_from_dict(ctx.active_object, focus_name, uv_map_as_dict)
            except Exception as excp:
                self.report({'ERROR'}, f"Failed to add UV map to mesh: {excp}")
                return {'CANCELLED'}

            # Set the new UV map as active
            uv_map = ctx.active_object.data.uv_layers.get(focus_name)
            if uv_map:
                _LOG.debug("Setting UV map as active.", focus_name)
                ctx.active_object.data.uv_layers.active = uv_map
                ctx.active_object.data.uv_layers[focus_name].active_render = True
            else:
                self.report({'ERROR'}, f"Failed to set UV map '{focus_name}' as active.")
                return {'CANCELLED'}
        else:
            focus_name = ctx.active_object.data.uv_layers[0].name

        # Add an ink layer to the material, get the relevant new nodes
        uvmap_node, texture_node, ink_layer_id = MaterialService.add_focus_nodes(material, uv_map_name=focus_name)

        if ctx.create_ink:
            # Create a new image instance and add it to the texture_node
            res = int(ctx.resolution)
            image = bpy.data.images.new(name="inkLayer" + str(ink_layer_id), width=res, height=res, alpha=True)
            image.generated_color = (1.0, 1.0, 1.0, 0.0)
            texture_node.image = image

        self.report({'INFO'}, f"Ink layer 'inkLayer{ink_layer_id}' added. Make sure to select it in the texture paint editor before painting.")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateInkOperator)
