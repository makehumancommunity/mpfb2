from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.entities.rig import Rig
from mpfb._classmanager import ClassManager
import bpy, json, math
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES

_LOG = LogService.get_logger("developer.operators.saverig")


class MPFB_OT_Save_Rig_Operator(bpy.types.Operator, ExportHelper):
    """Save rig definition as json"""
    bl_idname = "mpfb.save_rig"
    bl_label = "Save rig"
    bl_options = {'REGISTER'}

    filename_ext = '.json'

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

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(
            armature_object, mpfb_type_name="Basemesh")

        if basemesh is None:
            self.report({'ERROR'},
                        "Could not find related base mesh. It should have been parent or child of armature object.")
            return {'FINISHED'}

        rig_subrig = DEVELOPER_PROPERTIES.get_value("rig_subrig", entity_reference=context.scene)

        if rig_subrig:
            base_rig = ObjectService.find_object_of_type_amongst_nearest_relatives(
                armature_object, mpfb_type_name="Skeleton", only_parents=True)

            if base_rig is None:
                self.report({'ERROR'},
                            "Could not find related main skeleton. It should have been a parent of the armature.")
                return {'FINISHED'}

            child_meshes = list(ObjectService.find_deformed_child_meshes(armature_object))

            if len(child_meshes) != 1:
                self.report({'ERROR'},
                            "Could not find a unique deformed clothing mesh. It should be a child of the armature.")
                return {'FINISHED'}

            parent_rig = Rig.from_given_basemesh_and_armature(basemesh, base_rig, fast_positions=True)

            rig = Rig.from_given_basemesh_and_armature(child_meshes[0], armature_object, parent=parent_rig)

        else:
            rig = Rig.from_given_basemesh_and_armature(basemesh, armature_object)

        _LOG.dump("final rig_definition", rig.rig_definition)

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        with open(absolute_file_path, "w") as json_file:
            json.dump(rig.rig_definition, json_file, indent=4, sort_keys=True)
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
