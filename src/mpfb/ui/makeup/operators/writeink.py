"""Operator for writing an ink layer to the library."""

import bpy, os, json, gzip
from ....services import LocationService
from ....services import LogService
from ....services import ObjectService
from ....services import MaterialService
from ..makeuppanel import MAKEUP_PROPERTIES

from .... import ClassManager

_LOG = LogService.get_logger("makeup.writeink")


class MPFB_OT_WriteInkOperator(bpy.types.Operator):
    """Write a UV map to the local library. If there are multiple ink layers on the active object, use the first."""

    bl_idname = "mpfb.write_ink_layer"
    bl_label = "Write ink layer"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    @classmethod
    def poll(cls, context):
        """Check if the operator can run in the current context and that a mesh object is active."""
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        """Write ink layer to library."""
        mesh_object = context.active_object

        ink_layer_name = MAKEUP_PROPERTIES.get_value("ink_layer_name", entity_reference=context.scene)
        if not str(ink_layer_name).strip():
            self.report({'ERROR'}, "An ink layer name must be provided.")
            return {'CANCELLED'}

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

        uv_name, image_name = MaterialService.get_ink_layer_info(mesh_object)
        _LOG.debug("uv_name", uv_name)
        _LOG.debug("image_name", image_name)

        focus_name = str(uv_name).replace(" ", "_") + ".json.gz"
        focus_filename = os.path.join(LocationService.get_user_data("uv_layers"), focus_name)
        if not os.path.exists(focus_filename):
            focus_filename = os.path.join(LocationService.get_mpfb_data("uv_layers"), focus_name)
            if not os.path.exists(focus_filename):
                self.report({'ERROR'}, "The ink layer's focus could not be found in the library.")
                return {'CANCELLED'}

        inkpath = LocationService.get_user_data("ink_layers")
        if not os.path.exists(inkpath):
            os.makedirs(inkpath)

        ink_layer_fn = os.path.join(inkpath, str(ink_layer_name).replace(" ", "_") + ".json")
        image_fn = os.path.join(inkpath, str(ink_layer_name).replace(" ", "_") + ".png")

        ink_info = {
            "name": ink_layer_name,
            "focus": uv_name,
            "image_name": str(ink_layer_name).replace(" ", "_") + ".png"
            }

        bpy.data.images[image_name].save(filepath=image_fn)

        with open(ink_layer_fn, 'w') as f:
            json.dump(ink_info, f, indent=4)

        self.report({'INFO'}, f"Ink layer '{ink_layer_name}' written to library at {ink_layer_fn}.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_WriteInkOperator)
