from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
import bpy, json
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("developer.saverigifylayers")

class MPFB_OT_Save_Rigify_Layers_Operator(bpy.types.Operator, ExportHelper):
    """Save rigify layer definition as json"""
    bl_idname = "mpfb.save_rigify_layers"
    bl_label = "Save rigify layers"
    bl_options = {'REGISTER'}

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
        rigify_ui["selection_colors"] = dict()

        rigify_ui["rigify_colors_lock"] = armature_object.data.rigify_colors_lock
        rigify_ui["selection_colors"]["select"] = list(armature_object.data.rigify_selection_colors.select)
        rigify_ui["selection_colors"]["active"] = list(armature_object.data.rigify_selection_colors.active)

        rigify_ui["colors"] = []

        for color in armature_object.data.rigify_colors:
            col = dict()
            col["name"] = str(color.name)
            col["normal"] = color["normal"].to_list()
            rigify_ui["colors"].append(col)

        rigify_ui["layers"] = []
        for layer in armature_object.data.layers:
            rigify_ui["layers"].append(layer)

        rigify_ui["rigify_layers"] = []

        for rigify_layer in armature_object.data.rigify_layers:
            layer = dict()
            layer["name"] = rigify_layer.name
            layer["row"] = rigify_layer.row
            layer["selset"] = rigify_layer.selset
            layer["group"] = rigify_layer.group

            rigify_ui["rigify_layers"].append(layer)

        _LOG.dump("rigify_ui", rigify_ui)

        with open(absolute_file_path, "w") as json_file:
            json.dump(rigify_ui, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Rigify_Layers_Operator)
