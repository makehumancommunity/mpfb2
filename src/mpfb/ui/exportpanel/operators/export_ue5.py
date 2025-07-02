# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Operator responsible for export of Human mesh and hair cards to FBX hair assets to Alembic, optional parenting of card assets and merging of hair assets
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.locationservice import LocationService
from .... import ClassManager
import bpy,os,json

_LOG = LogService.get_logger("exportpanel.export_ue5")


class MPFB_OT_ExportUE5_Operator(bpy.types.Operator):
    """Exports Human model, cards and hair"""
    bl_idname = "mpfb.export_ue5"
    bl_label = "Export"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        export_name = getattr(scene, "export_object_name", "ExportedObject")
        export_path = bpy.path.abspath(getattr(scene, "export_save_path", "//exports/"))

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
            self.report({'ERROR'}, "No mesh 'Human' found.")
            return {'CANCELLED'}

        if not armature_root:
            self.report({'ERROR'}, "No armature 'root' found. Apply UE5 rig.")
            return {'CANCELLED'}

        # Make curve based hair visible
        for child in mesh_Human.children:
            if not( child.name.endswith("_cards") or child.name.endswith("_brace")):
                obj.hide_viewport = False

        # Export hair cards joined to Human mesh
        if getattr(scene, "join_hair_cards", False):

            # Hair, facial and eyebrow assets need to be treated separately so weights can be assinged better
            actual_dir = os.path.dirname(__file__)
            hair_properties_dir = os.path.join(actual_dir,"..","..", "haireditorpanel", "properties")
            json_files = ["hair_assets.json", "facial_assets.json", "eyebrow_assets.json"]
            head_hair_objects = []

            for json_file in json_files:
                file_path = os.path.join(hair_properties_dir, json_file)
                if not os.path.exists(file_path):
                    _LOG.warn(f"Hair property file not found: {file_path}")
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    for item in data.get("items", []):
                        asset_name = item[0]
                        head_hair_objects.append(f"{asset_name}_cards")

            card_head_objects = [obj for obj in bpy.data.objects if obj.name.endswith("_cards") and obj.name in head_hair_objects]
            card_objects = [obj for obj in bpy.data.objects if obj.name.endswith("_cards") and obj.name not in head_hair_objects]

            if not (card_objects or card_head_objects):
                self.report({'WARNING'}, "No hair card objects found.")
            else:
                bpy.ops.object.select_all(action='DESELECT')

                # Join all head card objects
                if card_head_objects:
                    for obj in card_head_objects:
                        obj.select_set(True)
                    context.view_layer.objects.active = card_head_objects[0]
                    bpy.ops.object.join()
                    card_head_object = context.active_object

                    card_head_object.select_set(False)

                # Join all body card objects
                if card_objects:
                    for obj in card_objects:
                        obj.select_set(True)
                    context.view_layer.objects.active = card_objects[0]
                    bpy.ops.object.join()
                    card_object = context.active_object

                # Turn off viewport visibilitz of Hide helpers modifier so it allows normal parenting
                bpy.ops.object.mode_set(mode='OBJECT')
                for mod in context.object.modifiers:
                    if "Hide helpers" in mod.name:
                        mod.show_viewport = False

                # Select all vertices on both card objects
                if card_objects:
                    bpy.ops.object.select_all(action='DESELECT')
                    mesh_Human.select_set(False)
                    armature_root.select_set(False)
                    card_object.select_set(True)
                    context.view_layer.objects.active = card_object
                    card_object = context.active_object
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    card_object.select_set(False)

                if card_head_objects:
                    bpy.ops.object.select_all(action='DESELECT')
                    card_head_object.select_set(True)
                    context.view_layer.objects.active = card_head_object
                    card_head_object = context.active_object
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    card_head_object.select_set(False)

                # Parent body card assets to root armature with envelope weights
                if card_objects:
                    bpy.ops.object.select_all(action='DESELECT')
                    mesh_Human.select_set(False)
                    armature_root.select_set(True)
                    card_object.select_set(True)
                    context.view_layer.objects.active = armature_root
                    bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
                    card_object.select_set(False)

                # Parent head card assets to root armature with automatic weights
                if card_head_objects:
                    mesh_Human.select_set(False)
                    armature_root.select_set(True)
                    card_head_object.select_set(True)
                    context.view_layer.objects.active = armature_root
                    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

                    # Force all vertices in head card object to have maximum weights by head bone
                    head_group = card_head_object.vertex_groups.get("head")
                    if not head_group:
                        head_group = card_head_object.vertex_groups.new(name="head")
                    verts = [v.index for v in card_head_object.data.vertices]
                    head_group.add(verts, 1.0, 'REPLACE')
                    card_head_object.select_set(False)

                # Join body card and head card objects
                if(card_head_objects and card_objects):
                    card_head_object.select_set(True)
                    card_object.select_set(True)
                    context.view_layer.objects.active = card_object
                    bpy.ops.object.join()
                elif not card_objects:
                    card_object=card_head_object

                # Join human and card object
                mesh_Human.select_set(True)
                card_object.select_set(True)
                context.view_layer.objects.active = mesh_Human
                bpy.ops.object.join()


                # Assign selected vertices to vertex group "body" so they are not hidden by HideHelpers modifier
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.vertex_group_set_active(group='body')
                bpy.ops.object.vertex_group_assign()

                # Return to object mode
                bpy.ops.object.mode_set(mode='OBJECT')

                # Turn on viewport visibilitz of Hide helpers modifier
                for mod in context.object.modifiers:
                    if "Hide helpers" in mod.name:
                        mod.show_viewport = True
        else:
            # Export hair cards separately from Human mesh, but joined together
            if getattr(scene, "join_hair_assets", False):
                card_objects = [obj for obj in bpy.data.objects if obj.name.endswith("_cards")]
                if not card_objects:
                    self.report({'WARNING'}, "No hair card objects to export.")
                else:
                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in card_objects:
                        obj.select_set(True)
                    context.view_layer.objects.active = card_objects[0]
                    bpy.ops.object.join()

                    bpy.ops.export_scene.fbx(
                        filepath=f"{export_path}{export_name}_haircards.fbx",
                        use_selection=True,
                        add_leaf_bones=False,
                        apply_unit_scale=True,
                        apply_scale_options='FBX_SCALE_ALL'
                    )
            else:
                # Export each card asset separately
                card_objects = [obj for obj in bpy.data.objects if obj.name.endswith("_cards")]
                for obj in card_objects:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    context.view_layer.objects.active = obj

                    bpy.ops.export_scene.fbx(
                        filepath=f"{export_path}{export_name}_{obj.name}.fbx",
                        use_selection=True,
                        add_leaf_bones=False,
                        apply_unit_scale=True,
                        apply_scale_options='FBX_SCALE_ALL'
                    )

        # Export hair curves
        if getattr(scene, "join_hair_assets", False):
            # Export hair assets together
            curve_objects = [child for child in mesh_Human.children if not( child.name.endswith("_cards") or child.name.endswith("_brace"))]
            if not curve_objects:
                self.report({'WARNING'}, "No curve-type children fof Human mesh found.")
            else:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in curve_objects:
                    obj.select_set(True)
                context.view_layer.objects.active = curve_objects[0]

                bpy.ops.wm.alembic_export(
                    filepath=f"{export_path}{export_name}_hair.abc",
                    selected=True,
                    flatten=False,
                    visible_objects_only=False
                )
        else:
            # Export each hair asset individually
            for child in mesh_Human.children:
                if not( child.name.endswith("_cards") or child.name.endswith("_brace")):
                    bpy.ops.object.select_all(action='DESELECT')
                    child.select_set(True)
                    context.view_layer.objects.active = child

                    bpy.ops.wm.alembic_export(
                        filepath=f"{export_path}{export_name}_{child.name}.abc",
                        selected=True,
                        flatten=False,
                        visible_objects_only=False
                    )

        # Select mesh and armature
        bpy.ops.object.select_all(action='DESELECT')
        mesh_Human.select_set(True)
        armature_root.select_set(True)
        context.view_layer.objects.active = armature_root

        # Export Human model to FBX (possibly with joined cards)
        bpy.ops.export_scene.fbx(
            filepath=f"{export_path}{export_name}.fbx",
            use_selection=True,
            add_leaf_bones=False,
            primary_bone_axis='X',
            secondary_bone_axis='-Z'
        )

        # Hide curve based hair
        for child in mesh_Human.children:
            if not( child.name.endswith("_cards") or child.name.endswith("_brace")):
                obj.hide_viewport = True

        self.report({'INFO'}, "Exporting character to UE5")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ExportUE5_Operator)