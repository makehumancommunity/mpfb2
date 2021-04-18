
from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb._classmanager import ClassManager
import bpy, json
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("loadnodes.operators.loadnodes")


class MPFB_OT_Load_Nodes_Operator(bpy.types.Operator, ImportHelper):
    """Load node tree from json"""
    bl_idname = "mpfb.load_nodes"
    bl_label = "Load nodes"
    bl_options = {'REGISTER'}

    filename_ext = '.json'

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            return not MaterialService.has_materials(context.active_object)
        return False

    def execute(self, context):
        _LOG.enter()
        _LOG.debug("click")

        blender_object = context.active_object
        if len(blender_object.material_slots) > 0:
            self.report({'ERROR'}, "This object already has a material")
            return {'FINISHED'}

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        as_dict = dict()

        with open(absolute_file_path, "r") as json_file:
            json_data = json_file.read()

            import time
            ts = int(time.time())

            json_data = str(json_data).replace("$group_name", "node_group." + str(ts))

            as_dict = json.loads(json_data)
            self.report({'INFO'}, "JSON data read")

        _LOG.dump("loaded json data", as_dict)

        material = MaterialService.create_empty_material("nodes_material", blender_object)
        NodeService.apply_node_tree_from_dict(material.node_tree, as_dict, True)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Nodes_Operator)
