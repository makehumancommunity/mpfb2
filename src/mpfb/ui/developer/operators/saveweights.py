from ....services import LogService
from ....services import MaterialService
from ....services import ObjectService
from ....services import RigService
from ....entities.rig import Rig
from .... import ClassManager
import bpy, json, math, re
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("developer.operators.saveweights")

class MPFB_OT_Save_Weights_Operator(bpy.types.Operator, ExportHelper):
    """Save weights as json"""
    bl_idname = "mpfb.save_weights"
    bl_label = "Save weights"
    bl_options = {'REGISTER'}

    filename_ext = '.mhw'
    check_extension = False

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if ObjectService.object_is_any_mesh(context.object):
            return True
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        return True

    def execute(self, context):
        _LOG.enter()

        subrig_object = None

        if ObjectService.object_is_any_mesh(context.object):
            basemesh = context.object
            armature_object = None

            for mod in basemesh.modifiers:
                if mod.type == 'ARMATURE':
                    if mod.vertex_group == "mhmask-subrig":
                        subrig_object = mod.object
                    elif not mod.vertex_group:
                        armature_object = mod.object

            if armature_object is None:
                self.report({'ERROR'}, "Could not find the related armature. The active mesh must have an Armature "
                                       "modifier that references it.")
                return {'FINISHED'}

        else:
            if context.object is None or context.object.type != 'ARMATURE':
                self.report({'ERROR'}, "Must have armature or basemesh as active object")
                return {'FINISHED'}

            armature_object = context.object
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature_object, mpfb_type_name="Basemesh")

            if basemesh is None:
                self.report({'ERROR'}, "Could not find related basemesh. It should have been parent or child of armature object.")
                return {'FINISHED'}

        from ...developer.developerpanel import DEVELOPER_PROPERTIES  # pylint: disable=C0415

        weights_mask = DEVELOPER_PROPERTIES.get_value("weights_mask", entity_reference=context.scene)
        save_evaluated = DEVELOPER_PROPERTIES.get_value("save_evaluated", entity_reference=context.scene)
        save_masks = DEVELOPER_PROPERTIES.get_value("save_masks", entity_reference=context.scene)

        if save_evaluated:
            eval_basemesh = basemesh.evaluated_get(context.view_layer.depsgraph)

            if len(eval_basemesh.data.vertices) != len(basemesh.data.vertices):
                self.report({'ERROR'}, "The evaluated mesh has a different vertex count")
                return {'FINISHED'}

            basemesh = eval_basemesh

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        armatures = []

        if weights_mask in ("SKELETON", "BOTH"):
            armatures.append(armature_object)

        if weights_mask in ("SUBRIG", "BOTH"):
            if not subrig_object:
                self.report({'ERROR'}, "Could not find the related sub-rig. The active mesh must have an Armature "
                                       "modifier with the 'mhmask-subrig' vertex group that references it.")
                return {'FINISHED'}

            armatures.append(subrig_object)

        weights = RigService.get_weights(
            armatures, basemesh, all_groups=(weights_mask == "ALL_GROUPS"), all_masks=save_masks)

        # Strip the Rigify deform bone prefix for convenience
        def strip_def(name):
            if name.startswith('DEF-'):
                # Only strip if a bone with that name existed in the metarig
                if any(('ORG-'+name[4:]) in arm.pose.bones for arm in armatures):
                    return name[4:]
            return name

        weights["weights"] = {strip_def(k): v for k,v in weights["weights"].items()}

        with open(absolute_file_path, "w") as json_file:
            json.dump(weights, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Weights_Operator)
