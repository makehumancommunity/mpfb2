"""Operator for saving a custom rig to the user library."""

import bpy, json, os, re

from ....services import LogService
from ....services import LocationService
from ....services import ObjectService
from ....services import RigService
from ....entities.rig import Rig
from .... import ClassManager

_LOG = LogService.get_logger("makerig.operators.savetolibrary")


class MPFB_OT_Save_Rig_To_Library_Operator(bpy.types.Operator):
    """Save the active armature as a named custom rig in the user library"""

    bl_idname = "mpfb.save_rig_to_library"
    bl_label = "Save rig to library"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'ARMATURE'

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object must be an armature")
            return {'FINISHED'}

        armature_object = context.object

        from ...makerig import MakeRigProperties  # pylint: disable=C0415
        scene = context.scene

        library_rig_name = MakeRigProperties.get_value("library_rig_name", entity_reference=scene)
        library_identifying_bones_str = MakeRigProperties.get_value("library_identifying_bones", entity_reference=scene)
        library_also_save_weights = MakeRigProperties.get_value("library_also_save_weights", entity_reference=scene)

        # Validate rig name
        if not library_rig_name or not re.match(r'^[a-zA-Z0-9_]+$', library_rig_name):
            self.report({'ERROR'}, "Library rig name must be non-empty and contain only letters, digits, and underscores")
            return {'FINISHED'}

        # Parse and validate identifying bones
        identifying_bones = [b.strip() for b in library_identifying_bones_str.split(",") if b.strip()]
        if not identifying_bones:
            self.report({'ERROR'}, "At least one identifying bone name is required")
            return {'FINISHED'}

        missing = [b for b in identifying_bones if b not in armature_object.data.bones]
        if missing:
            self.report({'ERROR'}, "Bones not found in armature: " + ", ".join(missing))
            return {'FINISHED'}

        # Warn if any identifying bone is a known built-in rig bone
        _builtin_indicator_bones = {
            "oculi02.R", "thumb_01_l", "breast_l", "RThumb", "mixamo:Hips", "LBigToe",
            "mixamorig:LeftHandThumb1", "mixamorig:LeftBreast", "brow.T.R.002",
            "ORG-clavicle_l", "ORG-brow.T.R.002", "ORG-toe2-1.L"
        }
        clashing = [b for b in identifying_bones if b in _builtin_indicator_bones]
        if clashing:
            self.report({'WARNING'}, "Some identifying bones are also used by built-in rigs: " + ", ".join(clashing))

        # Build rig definition
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        rig = Rig.from_given_armature_context(armature_object, operator=self, is_subrig=False, rigify_ui=False)
        if not rig:
            return {'FINISHED'}

        rig.rig_header["identifying_bones"] = identifying_bones

        # Determine output directory
        rigs_dir = LocationService.get_user_data("rigs")
        os.makedirs(rigs_dir, exist_ok=True)

        rig_file = os.path.join(rigs_dir, library_rig_name + ".json")
        with open(rig_file, "w") as f:
            json.dump(rig.rig_header, f, indent=4, sort_keys=True)

        self.report({'INFO'}, "Rig saved to " + rig_file)

        # Optionally save weights
        if library_also_save_weights:
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature_object, mpfb_type_name="Basemesh")
            if basemesh is None:
                self.report({'WARNING'}, "Could not find related basemesh; weights not saved")
            else:
                weights = RigService.get_weights([armature_object], basemesh, all_groups=False, all_masks=False)
                weights_file = os.path.join(rigs_dir, "weights." + library_rig_name + ".json")
                with open(weights_file, "w") as f:
                    json.dump(weights, f, indent=4, sort_keys=True)
                self.report({'INFO'}, "Weights saved to " + weights_file)

        # Invalidate cache so new rig is discoverable immediately
        from ....services import AssetService  # pylint: disable=C0415
        AssetService.invalidate_custom_rig_cache()

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Rig_To_Library_Operator)
