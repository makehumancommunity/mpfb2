from ....entities.objectproperties import GeneralObjectProperties
from ....services import LogService
from ....services import MaterialService
from ....services import ObjectService
from ....entities.rig import Rig
from .... import ClassManager
import bpy, json, math
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

from ...developer.developerpanel import DEVELOPER_PROPERTIES

_LOG = LogService.get_logger("developer.operators.saverig")


class MPFB_OT_Save_Rig_Operator(bpy.types.Operator, ExportHelper):
    """Save rig definition as json"""
    bl_idname = "mpfb.save_rig"
    bl_label = "Save rig"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.mpfbskel'
    check_extension = False

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        # TODO: check current mode
        return True

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        rig_subrig = DEVELOPER_PROPERTIES.get_value("rig_subrig", entity_reference=context.scene)
        rig_save_rigify = DEVELOPER_PROPERTIES.get_value("rig_save_rigify", entity_reference=context.scene)
        rig_refit = DEVELOPER_PROPERTIES.get_value("rig_refit", entity_reference=context.scene)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        rig = Rig.from_given_armature_context(
            armature_object, operator=self, is_subrig=bool(rig_subrig), rigify_ui=rig_save_rigify)

        if not rig:
            return {'FINISHED'}

        if rig_refit:
            rig.save_strategies(refit=True)
            rig.reposition_edit_bone(developer=True)

            object_type = "Subrig" if rig_subrig else "Skeleton"
            GeneralObjectProperties.set_value("object_type", object_type, entity_reference=armature_object)

        _LOG.dump("final rig_definition", rig.rig_definition)

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        with open(absolute_file_path, "w") as json_file:
            json.dump(rig.rig_header, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        unmatched_bone_names = rig.list_unmatched_bones()
        unmatched = len(unmatched_bone_names)

        if unmatched > 0:
            self.report({'WARNING'},
                        "There were " + str(unmatched) + " bones that could not be matched to cube or vertex")
            _LOG.warn("Unmatched bone names:", unmatched_bone_names)

        if rig.bad_constraint_targets:
            self.report({'WARNING'},
                        "There were " + str(len(rig.bad_constraint_targets)) + " bones with bad constraint targets")
            _LOG.warn("Bad target bone names:", list(rig.bad_constraint_targets))

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Rig_Operator)
