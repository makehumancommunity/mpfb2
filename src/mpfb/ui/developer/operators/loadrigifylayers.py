from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
import bpy, json
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("developer.loadrigifylayers")

class MPFB_OT_Load_Rigify_Layers_Operator(bpy.types.Operator, ImportHelper):
    """Load rigify layer definition as json"""
    bl_idname = "mpfb.load_rigify_layers"
    bl_label = "Load rigify layers"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.json'

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        # TODO: check that it is a rigify enabled rig
        return True

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        armature_object = bpy.context.active_object

        rigify_ui = dict()

        with open(absolute_file_path, "r") as json_file:
            rigify_ui = json.load(json_file)

        bpy.ops.armature.rigify_add_bone_groups()
        bpy.ops.pose.rigify_layer_init()

        armature_object.data.rigify_colors_lock = rigify_ui["rigify_colors_lock"]
        armature_object.data.rigify_selection_colors.select = rigify_ui["selection_colors"]["select"]
        armature_object.data.rigify_selection_colors.active = rigify_ui["selection_colors"]["active"]

        i = 0
        for color in armature_object.data.rigify_colors:
            col = rigify_ui["colors"][i]
            color.name = col["name"]
            color.normal = col["normal"]
            i = i + 1

        i = 0
        for rigify_layer in armature_object.data.layers:
            armature_object.data.layers[i] = rigify_ui["layers"][i]
            i = i + 1

        i = 0
        for rigify_layer in armature_object.data.rigify_layers:
            layer = rigify_ui["rigify_layers"][i]
            rigify_layer.name = layer["name"]
            rigify_layer.row = layer["row"]
            rigify_layer.selset = layer["selset"]
            rigify_layer.group = layer["group"]
            i = i + 1

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Rigify_Layers_Operator)
