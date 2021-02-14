#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb._classmanager import ClassManager
import bpy, json
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("savenodes.operators.savenodes")

class MPFB_OT_Save_Nodes_Operator(bpy.types.Operator, ExportHelper):
    """Save node tree as json"""
    bl_idname = "mpfb.save_nodes"
    bl_label = "Save nodes"
    bl_options = {'REGISTER'}

    filename_ext = '.json'

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            return MaterialService.has_materials(context.active_object)
        return False

    def execute(self, context):
        _LOG.enter()
        _LOG.debug("click")

        blender_object = context.active_object
        if len(blender_object.material_slots) < 1:
            self.report({'ERROR'}, "This object does not have any material")
            return {'FINISHED'}
        if len(blender_object.material_slots) > 1:
            self.report({'ERROR'}, "This object has more than one material")
            return {'FINISHED'}

        material = MaterialService.get_material(blender_object)
        _LOG.debug("material", material)

        as_dict = NodeService.get_node_tree_as_dict(material.node_tree)
        _LOG.dump("nodes", as_dict)

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        with open(absolute_file_path, "w") as json_file:
            json.dump(as_dict, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Save_Nodes_Operator)
