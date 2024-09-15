"""Operator for adding a makeup focus to a material."""

import bpy, os
from ....services import LocationService
from ....services import LogService
from ....services import ObjectService
from ....services import MaterialService
from ....services import MeshService
from ..makeuppanel import MAKEUP_PROPERTIES

from .... import ClassManager

_LOG = LogService.get_logger("makeup.addfocus")


class MPFB_OT_AddFocusOperator(bpy.types.Operator):
    """Add a new focus to the mesh's existing material. Only MakeSkin materials are supported."""

    bl_idname = "mpfb.add_focus"
    bl_label = "Add focus"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Check if the operator can run in the current context and that a mesh object is active."""
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        """Create a new UV map on the selected object, using the name set in the Makeup Properties."""
        mesh_object = context.active_object

        # Use MaterialService to check that the mesh object has a MakeSkin material
        if not MaterialService.has_materials(mesh_object):
            self.report({'ERROR'}, "The mesh object does not have any materials.")
            return {'CANCELLED'}

        material = MaterialService.get_material(mesh_object)
        if MaterialService.identify_material(material) != "makeskin":
            self.report({'ERROR'}, "Only MakeSkin materials are supported.")
            return {'CANCELLED'}

        focus_name = MAKEUP_PROPERTIES.get_value("focus_name", entity_reference=context.scene)
        if not focus_name:
            self.report({'ERROR'}, "A focus name must be chosen.")
            return {'CANCELLED'}

        focus_filename = os.path.join(LocationService.get_mpfb_data("makeup"), focus_name)

        MaterialService.add_focus_nodes(material, focus_filename)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_AddFocusOperator)
