# Operators Reference

This page is a complete index of every operator defined in the MPFB UI layer.
It is intended as a quick look-up table for developers who know which operator
they are looking for but need to find its source file, Blender identifier, or
documentation.

The table is sorted first by file path (relative to `src/mpfb/ui/`), then by
`bl_idname`. The **Class** column links to the section documentation where the
operator is described in detail. Operators in sections that have not yet been
documented appear with plain text class names.

| Path | `bl_idname` | `bl_label` | Class | Base class(es) |
|---|---|---|---|---|
| `apply_assets/assetlibrary/operators/installtarget.py` | `mpfb.install_target` | "Install custom target" | [MPFB_OT_Install_Target_Operator](apply_assets/assetlibrary.md) | `MpfbOperator`, `ImportHelper` |
| `apply_assets/assetlibrary/operators/loadlibraryclothes.py` | `mpfb.load_library_clothes` | "Load" | [MPFB_OT_Load_Library_Clothes_Operator](apply_assets/assetlibrary.md) | `MpfbOperator` |
| `apply_assets/assetlibrary/operators/loadlibraryink.py` | `mpfb.load_library_ink` | "Load" | [MPFB_OT_Load_Library_Ink_Operator](apply_assets/assetlibrary.md) | `MpfbOperator` |
| `apply_assets/assetlibrary/operators/loadlibrarymaterial.py` | `mpfb.load_library_material` | "Load" | [MPFB_OT_Load_Library_Material_Operator](apply_assets/assetlibrary.md) | `MpfbOperator` |
| `apply_assets/assetlibrary/operators/loadlibrarypose.py` | `mpfb.load_library_pose` | "Load Pose" | [MPFB_OT_Load_Library_Pose_Operator](apply_assets/assetlibrary.md) | `MpfbOperator` |
| `apply_assets/assetlibrary/operators/loadlibraryproxy.py` | `mpfb.load_library_proxy` | "Load" | [MPFB_OT_Load_Library_Proxy_Operator](apply_assets/assetlibrary.md) | `MpfbOperator` |
| `apply_assets/assetlibrary/operators/loadlibraryskin.py` | `mpfb.load_library_skin` | "Load" | [MPFB_OT_Load_Library_Skin_Operator](apply_assets/assetlibrary.md) | `MpfbOperator` |
| `apply_assets/assetlibrary/operators/loadpack.py` | `mpfb.load_pack` | "Load pack from zip file" | [MPFB_OT_Load_Pack_Operator](apply_assets/assetlibrary.md) | `MpfbOperator`, `ImportHelper` |
| `apply_assets/assetlibrary/operators/unloadlibraryclothes.py` | `mpfb.unload_library_clothes` | "Unequip" | [MPFB_OT_Unload_Library_Clothes_Operator](apply_assets/assetlibrary.md) | `MpfbOperator` |
| `apply_assets/loadclothes/operators/loadclothes.py` | `mpfb.load_clothes` | "Load clothes from file" | [MPFB_OT_Load_Clothes_Operator](apply_assets/loadclothes.md) | `bpy.types.Operator`, `ImportHelper` |
| `create_assets/makeclothes/operators/bmxref.py` | `mpfb.basemesh_xref` | "Create xref cache" | [MPFB_OT_BasemeshXrefOperator](create_assets/makeclothes.md) | `MpfbOperator` |
| `create_assets/makeclothes/operators/checkclothes.py` | `mpfb.check_makeclothes_clothes` | "Check" | [MPFB_OT_CheckClothesOperator](create_assets/makeclothes.md) | `MpfbOperator` |
| `create_assets/makeclothes/operators/extractclothes.py` | `mpfb.extract_makeclothes_clothes` | "Extract clothes" | [MPFB_OT_ExtractClothesOperator](create_assets/makeclothes.md) | `MpfbOperator` |
| `create_assets/makeclothes/operators/gendelete.py` | `mpfb.makeclothes_gendelete` | "Interpolate" | [MPFB_OT_GenDeleteOperator](create_assets/makeclothes.md) | `MpfbOperator` |
| `create_assets/makeclothes/operators/genuuid.py` | `mpfb.genuuid` | "Generate UUID" | [MPFB_OT_GenerateUUIDOperator](create_assets/makeclothes.md) | `MpfbOperator` |
| `create_assets/makeclothes/operators/legacyimport.py` | `mpfb.legacy_makeclothes_import` | "Import legacy props" | [MPFB_OT_LegacyImportOperator](create_assets/makeclothes.md) | `MpfbOperator` |
| `create_assets/makeclothes/operators/markclothes.py` | `mpfb.mark_makeclothes_clothes` | "Change type" | [MPFB_OT_MarkClothesOperator](create_assets/makeclothes.md) | `MpfbOperator` |
| `create_assets/makeclothes/operators/writeclothes.py` | `mpfb.write_makeclothes_clothes` | "Save as files" | [MPFB_OT_WriteClothesOperator](create_assets/makeclothes.md) | `MpfbOperator`, `ClothesCommon`, `ExportHelper` |
| `create_assets/makeclothes/operators/writeclotheslibrary.py` | `mpfb.write_makeclothes_library` | "Store in library" | [MPFB_OT_WriteClothesLibraryOperator](create_assets/makeclothes.md) | `MpfbOperator`, `ClothesCommon` |
| `create_assets/makepose/operators/loadanimation.py` | `mpfb.load_animation` | "Load animation" | [MPFB_OT_Load_Animation_Operator](create_assets/makepose.md) | `MpfbOperator` |
| `create_assets/makepose/operators/saveanimation.py` | `mpfb.save_animation` | "Save animation" | [MPFB_OT_Save_Animation_Operator](create_assets/makepose.md) | `MpfbOperator` |
| `create_assets/makepose/operators/savepose.py` | `mpfb.save_pose` | "Save pose" | [MPFB_OT_Save_Pose_Operator](create_assets/makepose.md) | `MpfbOperator` |
| `create_assets/makerig/operators/autotransferweights.py` | `mpfb.auto_transfer_weights` | "Auto transfer weights" | [MPFB_OT_Auto_Transfer_Weights_Operator](create_assets/makerig.md) | `MpfbOperator` |
| `create_assets/makerig/operators/loadrig.py` | `mpfb.load_rig` | "Load rig" | [MPFB_OT_Load_Rig_Operator](create_assets/makerig.md) | `MpfbOperator`, `ImportHelper` |
| `create_assets/makerig/operators/loadweights.py` | `mpfb.load_weights` | "Load weights" | [MPFB_OT_Load_Weights_Operator](create_assets/makerig.md) | `MpfbOperator`, `ImportHelper` |
| `create_assets/makerig/operators/movetocube.py` | `mpfb.move_bone_to_cube` | "Move to cubes" | [MPFB_OT_Move_To_Cube_Operator](create_assets/makerig.md) | `MpfbOperator` |
| `create_assets/makerig/operators/saverig.py` | `mpfb.save_rig` | "Save rig" | [MPFB_OT_Save_Rig_Operator](create_assets/makerig.md) | `MpfbOperator`, `ExportHelper` |
| `create_assets/makerig/operators/savetolibrary.py` | `mpfb.save_rig_to_library` | "Save rig to library" | [MPFB_OT_Save_Rig_To_Library_Operator](create_assets/makerig.md) | `MpfbOperator` |
| `create_assets/makerig/operators/saveweights.py` | `mpfb.save_weights` | "Save weights" | [MPFB_OT_Save_Weights_Operator](create_assets/makerig.md) | `MpfbOperator`, `ExportHelper` |
| `create_assets/makeskin/operators/creatematerial.py` | `mpfb.create_makeskin_material` | "Create material" | [MPFB_OT_CreateMaterialOperator](create_assets/makeskin.md) | `MpfbOperator` |
| `create_assets/makeskin/operators/importmaterial.py` | `mpfb.import_makeskin_material` | "Import material" | [MPFB_OT_ImportMaterialOperator](create_assets/makeskin.md) | `MpfbOperator`, `ImportHelper` |
| `create_assets/makeskin/operators/writealternate.py` | `mpfb.write_alternate` | "Store as alternate" | [MPFB_OT_WriteAlternateOperator](create_assets/makeskin.md) | `MpfbOperator` |
| `create_assets/makeskin/operators/writelibrary.py` | `mpfb.write_makeskin_to_library` | "Store as skin" | [MPFB_OT_WriteLibraryOperator](create_assets/makeskin.md) | `MpfbOperator` |
| `create_assets/makeskin/operators/writematerial.py` | `mpfb.write_makeskin_material` | "Save as MHMAT" | [MPFB_OT_WriteMaterialOperator](create_assets/makeskin.md) | `MpfbOperator`, `ExportHelper` |
| `create_assets/maketarget/operators/createtarget.py` | `mpfb.create_maketarget_target` | "Create target" | [MPFB_OT_CreateTargetOperator](create_assets/maketarget.md) | `MpfbOperator` |
| `create_assets/maketarget/operators/importptarget.py` | `mpfb.import_maketarget_ptarget` | "Import proxy-specific target" | [MPFB_OT_ImportPtargetOperator](create_assets/maketarget.md) | `MpfbOperator`, `ImportHelper` |
| `create_assets/maketarget/operators/importtarget.py` | `mpfb.import_maketarget_target` | "Import target" | [MPFB_OT_ImportTargetOperator](create_assets/maketarget.md) | `MpfbOperator`, `ImportHelper` |
| `create_assets/maketarget/operators/printtarget.py` | `mpfb.print_maketarget_target` | "Print target" | [MPFB_OT_PrintTargetOperator](create_assets/maketarget.md) | `MpfbOperator` |
| `create_assets/maketarget/operators/symmetrizeleft.py` | `mpfb.symmetrize_maketarget_left` | "Copy -x to +x" | [MPFB_OT_SymmetrizeLeftOperator](create_assets/maketarget.md) | `MpfbOperator` |
| `create_assets/maketarget/operators/symmetrizeright.py` | `mpfb.symmetrize_maketarget_right` | "Copy +x to -x" | [MPFB_OT_SymmetrizeRightOperator](create_assets/maketarget.md) | `MpfbOperator` |
| `create_assets/maketarget/operators/writelibtarget.py` | `mpfb.write_library_target` | "Save target" | [MPFB_OT_WriteLibTargetOperator](create_assets/maketarget.md) | `MpfbOperator` |
| `create_assets/maketarget/operators/writeptarget.py` | `mpfb.write_maketarget_ptarget` | "Save proxy-specific target" | [MPFB_OT_WritePtargetOperator](create_assets/maketarget.md) | `MpfbOperator`, `ExportHelper` |
| `create_assets/maketarget/operators/writetarget.py` | `mpfb.write_maketarget_target` | "Save target" | [MPFB_OT_WriteTargetOperator](create_assets/maketarget.md) | `MpfbOperator`, `ExportHelper` |
| `create_assets/makeup/operators/createink.py` | `mpfb.create_ink` | "Create ink" | [MPFB_OT_CreateInkOperator](create_assets/makeup.md) | `MpfbOperator` |
| `create_assets/makeup/operators/createuvmap.py` | `mpfb.create_uv_map` | "Create UV map" | [MPFB_OT_CreateUvMapOperator](create_assets/makeup.md) | `MpfbOperator` |
| `create_assets/makeup/operators/importuvmap.py` | `mpfb.import_uv_map` | "Import UV map" | [MPFB_OT_ImportUvMapOperator](create_assets/makeup.md) | `MpfbOperator`, `ImportHelper` |
| `create_assets/makeup/operators/writeink.py` | `mpfb.write_ink_layer` | "Write ink layer" | [MPFB_OT_WriteInkOperator](create_assets/makeup.md) | `MpfbOperator` |
| `create_assets/makeup/operators/writeuvmap.py` | `mpfb.write_uv_map` | "Write UV map" | [MPFB_OT_WriteUvMapOperator](create_assets/makeup.md) | `MpfbOperator`, `ExportHelper` |
| `create_assets/makeweight/operators/importweights.py` | `mpfb.import_makeweight_weight` | "Import weights" | [MPFB_OT_ImportWeightsOperator](create_assets/makeweight.md) | `MpfbOperator`, `ImportHelper` |
| `create_assets/makeweight/operators/saveweights.py` | `mpfb.save_makeweight_weight` | "Save weights" | [MPFB_OT_SaveWeightsOperator](create_assets/makeweight.md) | `MpfbOperator`, `ExportHelper` |
| `create_assets/makeweight/operators/symmetrizeleft.py` | `mpfb.symmetrize_makeweight_left` | "Copy right to left" | [MPFB_OT_SymmetrizeLeftOperator](create_assets/makeweight.md) | `MpfbOperator` |
| `create_assets/makeweight/operators/symmetrizeright.py` | `mpfb.symmetrize_makeweight_right` | "Copy left to right" | [MPFB_OT_SymmetrizeRightOperator](create_assets/makeweight.md) | `MpfbOperator` |
| `create_assets/makeweight/operators/truncateweights.py` | `mpfb.truncate_weights` | "Truncate" | [MPFB_OT_TruncateWeightsOperator](create_assets/makeweight.md) | `MpfbOperator` |
| `developer/operators/create_groups.py` | `mpfb.create_groups` | "Create groups" | [MPFB_OT_Create_Groups_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/destroygroups.py` | `mpfb.destroy_groups` | "Destroy Groups" | [MPFB_OT_Destroy_Groups_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/exportlog.py` | `mpfb.export_log` | "Export log" | [MPFB_OT_Export_Log_Operator](developer/developer.md) | `MpfbOperator`, `ExportHelper` |
| `developer/operators/listloglevels.py` | `mpfb.list_log_levels` | "List log levels" | [MPFB_OT_List_Log_Levels_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/loadnodes.py` | `mpfb.load_nodes` | "Load nodes" | [MPFB_OT_Load_Nodes_Operator](developer/developer.md) | `MpfbOperator`, `ImportHelper` |
| `developer/operators/loadtarget.py` | `mpfb.load_target` | "Load targets" | [MPFB_OT_Load_Target_Operator](developer/developer.md) | `MpfbOperator`, `ImportHelper` |
| `developer/operators/replacewithskin.py` | `mpfb.replace_with_skin` | "Skin" | [MPFB_OT_Replace_With_Skin_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/resetloglevels.py` | `mpfb.reset_log_levels` | "Reset log levels" | [MPFB_OT_Reset_Log_Levels_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/rewritenodetypes.py` | `mpfb.rewrite_node_types` | "Rewrite node types" | [MPFB_OT_Rewrite_Node_Types_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/savenodes.py` | `mpfb.save_nodes` | "Save nodes" | [MPFB_OT_Save_Nodes_Operator](developer/developer.md) | `MpfbOperator`, `ExportHelper` |
| `developer/operators/savetarget.py` | `mpfb.save_target` | "Save target" | [MPFB_OT_Save_Target_Operator](developer/developer.md) | `MpfbOperator`, `ExportHelper` |
| `developer/operators/setloglevel.py` | `mpfb.set_log_level` | "Set log level" | [MPFB_OT_Set_Log_Level_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/unittests.py` | `mpfb.unit_tests` | "Run unit tests" | [MPFB_OT_Unit_Tests_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/writecomposite.py` | `mpfb.write_composite` | "Write composite" | [MPFB_OT_Write_Composite_Operator](developer/developer.md) | `MpfbOperator` |
| `developer/operators/writematerial.py` | `mpfb.write_material` | "Write material" | [MPFB_OT_Write_Material_Operator](developer/developer.md) | `MpfbOperator` |
| `haireditorpanel/operators/apply_fur_operator.py` | `mpfb.apply_fur_operator` | "Apply fur" | MPFB_OT_ApplyFur_Operator | `bpy.types.Operator` |
| `haireditorpanel/operators/apply_hair_operator.py` | `mpfb.apply_hair_operator` | "Apply hair" | MPFB_OT_ApplyHair_Operator | `bpy.types.Operator` |
| `haireditorpanel/operators/apply_material_operator.py` | `mpfb.apply_material_operator` | "Apply material" | MPFB_OT_ApplyMaterial_Operator | `bpy.types.Operator` |
| `haireditorpanel/operators/bake_hair_operator.py` | `mpfb.bake_hair_operator` | "Bake hair cards" | MPFB_OT_BakeHair_Operator | `bpy.types.Operator` |
| `haireditorpanel/operators/delete_hair_operator.py` | `mpfb.delete_hair_operator` | "Delete hair" | MPFB_OT_DeleteHair_Operator | `bpy.types.Operator` |
| `haireditorpanel/operators/generate_hair_cards_operator.py` | `mpfb.generate_hair_cards_operator` | "Generate hair cards" | MPFB_OT_GenerateHairCards_Operator | `bpy.types.Operator` |
| `haireditorpanel/operators/setup_hair_operator.py` | `mpfb.setup_hair_operator` | "Setup hair" | MPFB_OT_SetupHair_Operator | `bpy.types.Operator` |
| `model/operators/prunehuman.py` | `mpfb.prune_human` | "Prune shapekeys" | [MPFB_OT_PruneHumanOperator](model/model.md) | `MpfbOperator` |
| `model/operators/refithuman.py` | `mpfb.refit_human` | "Refit assets to basemesh" | [MPFB_OT_RefitHumanOperator](model/model.md) | `MpfbOperator` |
| `new_human/importer/operators/importhuman.py` | `mpfb.importer_import_body` | "Import human" | [MPFB_OT_ImportHumanOperator](new_human/importer.md) | `MpfbOperator` |
| `new_human/importerpresets/operators/loadpresets.py` | `mpfb.importerpresets_load_importer_presets` | "Load selected presets" | [MPFB_OT_LoadImporterPresetsOperator](new_human/importerpresets.md) | `MpfbOperator` |
| `new_human/importerpresets/operators/overwritepresets.py` | `mpfb.importerpresets_overwrite_importer_presets` | "Overwrite selected presets" | [MPFB_OT_OverwriteImporterPresetsOperator](new_human/importerpresets.md) | `MpfbOperator` |
| `new_human/importerpresets/operators/savenewpresets.py` | `mpfb.importerpresets_save_new_importer_presets` | "Save new importer presets" | [MPFB_OT_SaveNewImporterPresetsOperator](new_human/importerpresets.md) | `MpfbOperator` |
| `new_human/newhuman/operators/createhuman.py` | `mpfb.create_human` | "Create human" | [MPFB_OT_CreateHumanOperator](new_human/newhuman.md) | `MpfbOperator` |
| `new_human/newhuman/operators/humanfrommhm.py` | `mpfb.human_from_mhm` | "Import MHM" | [MPFB_OT_HumanFromMHMOperator](new_human/newhuman.md) | `MpfbOperator`, `ImportHelper` |
| `new_human/newhuman/operators/humanfrompresets.py` | `mpfb.human_from_presets` | "Create human" | [MPFB_OT_HumanFromPresetsOperator](new_human/newhuman.md) | `MpfbOperator` |
| `operations/ai/operators/addvisiblebones.py` | `mpfb.openpose_visible_bones` | "Add OpenPose visible bones" | [MPFB_OT_OpenPose_Visible_Bones_Operator](operations/ai.md) | `MpfbOperator` |
| `operations/ai/operators/boundingbox.py` | `mpfb.boundingbox` | "From active" | [MPFB_OT_Boundingbox_Operator](operations/ai.md) | `MpfbOperator` |
| `operations/ai/operators/saveopenpose.py` | `mpfb.save_openpose` | "Save openpose" | [MPFB_OT_Save_Openpose_Operator](operations/ai.md) | `MpfbOperator`, `ExportHelper` |
| `operations/ai/operators/scenesettings.py` | `mpfb.openpose_scene_settings` | "Change scene settings" | [MPFB_OT_OpenPose_Scene_Settings_Operator](operations/ai.md) | `MpfbOperator` |
| `operations/animops/operators/makecyclic.py` | `mpfb.make_cyclic` | "Make cyclic" | [MPFB_OT_Make_Cyclic_Operator](operations/animops.md) | `MpfbOperator` |
| `operations/animops/operators/mapmixamo.py` | `mpfb.map_mixamo` | "Snap to mixamo" | [MPFB_OT_Map_Mixamo_Operator](operations/animops.md) | `MpfbOperator` |
| `operations/animops/operators/reduceddoll.py` | `mpfb.reduced_doll` | "Mixamo reduced doll" | [MPFB_OT_Reduced_Doll_Operator](operations/animops.md) | `MpfbOperator` |
| `operations/animops/operators/repeatanim.py` | `mpfb.repeat_animation` | "Repeat animation" | [MPFB_OT_Repeat_Animation_Operator](operations/animops.md) | `MpfbOperator` |
| `operations/basemeshops/operators/addcorrectivesmooth.py` | `mpfb.add_corrective_smooth` | "Add Corrective Smooth" | [MPFB_OT_Add_Corrective_Smooth_Operator](operations/basemeshops.md) | `MpfbOperator` |
| `operations/basemeshops/operators/bakeshapekeys.py` | `mpfb.bake_shapekeys` | "Bake shapekeys" | [MPFB_OT_Bake_Shapekeys_Operator](operations/basemeshops.md) | `MpfbOperator` |
| `operations/basemeshops/operators/deletehelpers.py` | `mpfb.delete_helpers` | "Delete helpers" | [MPFB_OT_Delete_Helpers_Operator](operations/basemeshops.md) | `MpfbOperator` |
| `operations/boneops/operators/copy_connected_strategy.py` | `mpfb.copy_connected_strategy` | "Copy Connected Strategies" | [MPFB_OT_Copy_Connected_Strategy_Operator](operations/boneops.md) | `AbstractBoneOperator` |
| `operations/boneops/operators/reapply_strategy.py` | `mpfb.reapply_strategy` | "Reapply Strategy" | [MPFB_OT_Reapply_Bone_Strategy_Operator](operations/boneops.md) | `AbstractBoneOperator` |
| `operations/boneops/operators/save_strategy_vertices.py` | `mpfb.save_strategy_vertices` | "Save Vertices" | [MPFB_OT_Save_Strategy_Vertices_Operator](operations/boneops.md) | `AbstractBoneOperator` |
| `operations/boneops/operators/set_bone_end_offset.py` | `mpfb.set_bone_end_offset` | "Set Bone End Offset" | [MPFB_OT_Set_Bone_End_Offset_Operator](operations/boneops.md) | `AbstractBoneOperator` |
| `operations/boneops/operators/set_bone_end_strategy.py` | `mpfb.set_bone_end_strategy` | "Set Bone End Strategy" | [MPFB_OT_Set_Bone_End_Strategy_Operator](operations/boneops.md) | `AbstractBoneOperator` |
| `operations/boneops/operators/set_roll_strategy.py` | `mpfb.set_roll_strategy` | "Set Roll Strategy" | [MPFB_OT_Set_Roll_Strategy_Operator](operations/boneops.md) | `AbstractBoneOperator` |
| `operations/boneops/operators/show_strategy_vertices.py` | `mpfb.show_strategy_vertices` | "Show Strategy Vertices" | [MPFB_OT_Show_Strategy_Vertices_Operator](operations/boneops.md) | `AbstractBoneOperator` |
| `operations/exportops/operators/createexportcopy.py` | `mpfb.export_copy` | "Create export copy" | [MPFB_OT_Create_Export_Copy_Operator](operations/exportops.md) | `MpfbOperator` |
| `operations/faceops/operators/configurelipsync.py` | `mpfb.configure_lip_sync` | "Assign Lip Sync shape keys" | [MPFB_OT_Configure_Lip_Sync_Operator](operations/faceops.md) | `MpfbOperator` |
| `operations/faceops/operators/loadfaceshapekeys.py` | `mpfb.load_face_shape_keys` | "Load face shape keys" | [MPFB_OT_Load_Face_Shape_Keys_Operator](operations/faceops.md) | `MpfbOperator` |
| `operations/matops/operators/createv2skin.py` | `mpfb.create_v2_skin` | "Create v2 skin" | [MPFB_OT_Create_V2_Skin_Operator](operations/matops.md) | `MpfbOperator` |
| `operations/matops/operators/removemakeup.py` | `mpfb.remove_makeup` | "Remove makeup" | [MPFB_OT_Remove_Makeup_Operator](operations/matops.md) | `MpfbOperator` |
| `operations/matops/operators/setnormalmap.py` | `mpfb.set_normalmap` | "Set normalmap" | [MPFB_OT_Set_Normalmap_Operator](operations/matops.md) | `MpfbOperator`, `ImportHelper` |
| `operations/poseops/operators/apply_pose.py` | `mpfb.apply_pose` | "Apply as rest pose" | [MPFB_OT_Apply_Pose_Operator](operations/poseops.md) | `MpfbOperator` |
| `operations/poseops/operators/copy_pose.py` | `mpfb.copy_pose` | "Copy pose" | [MPFB_OT_Copy_Pose_Operator](operations/poseops.md) | `MpfbOperator` |
| `operations/sculpt/operators/setupsculpt.py` | `mpfb.setup_sculpt` | "Set up mesh for sculpt" | [MPFB_OT_Setup_Sculpt_Operator](operations/sculpt.md) | `MpfbOperator` |
| `presets/enhancedsettings/operators/applysettings.py` | `mpfb.enhancedsettings_apply_settings` | "Apply selected presets" | [MPFB_OT_ApplyEnhancedSettingsOperator](presets/enhancedsettings.md) | `MpfbOperator` |
| `presets/enhancedsettings/operators/overwritesettings.py` | `mpfb.overwrite_enhanced_settings` | "Overwrite settings" | [MPFB_OT_OverwriteEnhancedSettingsOperator](presets/enhancedsettings.md) | `MpfbOperator` |
| `presets/enhancedsettings/operators/savenewsettings.py` | `mpfb.save_new_enhanced_settings` | "Save new settings" | [MPFB_OT_SaveNewEnhancedSettingsOperator](presets/enhancedsettings.md) | `MpfbOperator` |
| `presets/eyesettings/operators/applysettings.py` | `mpfb.eyesettings_apply_settings` | "Apply selected presets" | [MPFB_OT_ApplyEyeSettingsOperator](presets/eyesettings.md) | `MpfbOperator` |
| `presets/eyesettings/operators/overwritesettings.py` | `mpfb.overwrite_eye_settings` | "Overwrite settings" | [MPFB_OT_OverwriteEyeSettingsOperator](presets/eyesettings.md) | `MpfbOperator` |
| `presets/eyesettings/operators/savenewsettings.py` | `mpfb.save_new_eye_settings` | "Save new settings" | [MPFB_OT_SaveNewEyeSettingsOperator](presets/eyesettings.md) | `MpfbOperator` |
| `presets/humanpresets/operators/overwritepresets.py` | `mpfb.overwrite_human_presets` | "Overwrite presets" | [MPFB_OT_Overwrite_Human_Presets_Operator](presets/humanpresets.md) | `MpfbOperator` |
| `presets/humanpresets/operators/savenewpresets.py` | `mpfb.save_new_human_presets` | "Save new presets" | [MPFB_OT_Save_New_Presets_Operator](presets/humanpresets.md) | `MpfbOperator` |
| `presets/makeuppresets/operators/loadpresets.py` | `mpfb.load_makeup_presets` | "Load presets" | [MPFB_OT_Load_Makeup_Presets_Operator](presets/makeuppresets.md) | `generic_makeup_presets` |
| `presets/makeuppresets/operators/overwritepresets.py` | `mpfb.overwrite_makeup_presets` | "Overwrite presets" | [MPFB_OT_Overwrite_Makeup_Presets_Operator](presets/makeuppresets.md) | `generic_makeup_presets` |
| `presets/makeuppresets/operators/savenewpresets.py` | `mpfb.save_new_makeup_presets` | "Save new presets" | [MPFB_OT_Save_New_Makeup_Presets_Operator](presets/makeuppresets.md) | `generic_makeup_presets` |
| `rigging/addcycle/operators/loadcycle.py` | `mpfb.load_walk_cycle` | "Load walk cycle" | [MPFB_OT_Load_Walk_Cycle_Operator](rigging/addcycle.md) | `MpfbOperator` |
| `rigging/addrig/operators/addcustomrig.py` | `mpfb.add_custom_rig` | "Add custom rig" | [MPFB_OT_Add_Custom_Rig_Operator](rigging/addrig.md) | `MpfbOperator` |
| `rigging/addrig/operators/addrigifyrig.py` | `mpfb.add_rigify_rig` | "Add rigify rig" | [MPFB_OT_AddRigifyRigOperator](rigging/addrig.md) | `MpfbOperator` |
| `rigging/addrig/operators/addstandardrig.py` | `mpfb.add_standard_rig` | "Add standard rig" | [MPFB_OT_AddStandardRigOperator](rigging/addrig.md) | `MpfbOperator` |
| `rigging/addrig/operators/generaterigifyrig.py` | `mpfb.generate_rigify_rig` | "Generate" | [MPFB_OT_GenerateRigifyRigOperator](rigging/addrig.md) | `MpfbOperator` |
| `rigging/applypose/operators/loadmhbvh.py` | `mpfb.load_mhbvh_pose` | "Import MH BVH Pose" | [MPFB_OT_Load_MH_BVH_Operator](rigging/applypose.md) | `MpfbOperator`, `ImportHelper` |
| `rigging/applypose/operators/loadpartial.py` | `mpfb.load_partial` | "Load partial pose" | [MPFB_OT_Load_Partial_Operator](rigging/applypose.md) | `MpfbOperator` |
| `rigging/applypose/operators/loadpose.py` | `mpfb.load_pose` | "Load pose" | [MPFB_OT_Load_Pose_Operator](rigging/applypose.md) | `MpfbOperator` |
| `rigging/righelpers/operators/addhelpers.py` | `mpfb.add_helpers` | "Add helpers" | [MPFB_OT_AddHelpersOperator](rigging/righelpers.md) | `MpfbOperator` |
| `rigging/righelpers/operators/removehelpers.py` | `mpfb.remove_helpers` | "Remove helpers" | [MPFB_OT_RemoveHelpersOperator](rigging/righelpers.md) | `MpfbOperator` |
| `rigging/rigify/operators/converttorigify.py` | `mpfb.convert_to_rigify` | "Rigify" | [MPFB_OT_Convert_To_Rigify_Operator](rigging/rigify.md) | `MpfbOperator` |
| `system/dirresources/operators/dirresource.py` | `mpfb.dir_resource` | "Open" | [MPFB_OT_Dir_Resource_Operator](system/dirresources.md) | `MpfbOperator` |
| `system/webresources/operators/webresource.py` | `mpfb.web_resource` | "Open" | [MPFB_OT_Web_Resource_Operator](system/webresources.md) | `MpfbOperator` |
