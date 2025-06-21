# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Operator responsible for rescaling human armature and model for correct export and setting up attributes for export
# NOTE:         Previously used only for rescaling, therefore the name
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.locationservice import LocationService
from .... import ClassManager
import bpy, os

_LOG = LogService.get_logger("exportpanel.rescale_ue5")

class MPFB_OT_RescaleUE5_Operator(bpy.types.Operator):
    """Rescale model and armature so it works with UE5 mannequin and setup scene attributes for exporter"""
    bl_idname = "mpfb.rescale_ue5"
    bl_label = "Rescale"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Get default export destination
        actual_dir = os.path.dirname(__file__)
        default_dir = os.path.join(actual_dir, "../../../data/user_export/")

        # Find mesh
        mesh_Human = None
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and "Human" in obj.name:
                mesh_Human = obj
                break

        # Find armature
        armature_root = None
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and "root" in obj.name:
                armature_root = obj
                break

        # Check if they exist
        if not mesh_Human:
            self.report({'ERROR'}, "No mesh object with 'Human' in its name found.")
            return {'CANCELLED'}

        if not armature_root:
            self.report({'ERROR'}, "No armature object with 'root' in its name found.")
            return {'CANCELLED'}

        # Scale mesh 100x in Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        mesh_Human.select_set(True)
        context.view_layer.objects.active = mesh_Human
        bpy.ops.transform.resize(value=(100, 100, 100))

        # Snap 3D Cursor to World Origin
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

        # Scale armature 100x in Edit Mode relative to 3D Cursor
        bpy.ops.object.select_all(action='DESELECT')
        armature_root.select_set(True)
        context.view_layer.objects.active = armature_root
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.transform.resize(value=(100, 100, 100), center_override=(0.0, 0.0, 0.0))
        bpy.ops.object.mode_set(mode='OBJECT')

        # Scale armature 0.01x in Object Mode (together with mesh)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        armature_root.select_set(True)
        context.view_layer.objects.active = armature_root
        bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))

        # Set up properties for UI
        prop_id = f"mesh_rescaled_for_export"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.BoolProperty(
                name=prop_id,
                description=f"Has object been rescaled?",
                default=True
                )
            )
        prop_id = f"join_hair_cards"
        if not hasattr(bpy.types.Scene, "join_hair_cards"):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.BoolProperty(
                name=prop_id,
                description=f"Join hair cards with mesh before export?",
                default=True
                )
            )
        prop_id = f"join_hair_assets"
        if not hasattr(bpy.types.Scene, "join_hair_assets"):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.BoolProperty(
                name=prop_id,
                description=f"Merge all hair assets when exporting?",
                default=True
                )
            )

        prop_id = f"export_object_name"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.StringProperty(
                    name=prop_id,
                    description="Name to use for exported files",
                    default="MyHuman"
                )
            )

        prop_id = f"export_save_path"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.StringProperty(
                    name=prop_id,
                    description="Directory to save exported files",
                    subtype='DIR_PATH',
                    default=default_dir
                )
            )

        self.report({'INFO'}, "Object succesfuly rescaled for UE5 export.")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_RescaleUE5_Operator)