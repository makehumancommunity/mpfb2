"""Operator for importing MHCLO clothes."""

import bpy, os
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.materialservice import MaterialService
from mpfb.services.rigservice import RigService
from mpfb.entities.mhclo import Mhclo
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb import ClassManager

_LOG = LogService.get_logger("loadclothes.loadclothes")
_LOG.set_level(LogService.DUMP)

class MPFB_OT_Load_Clothes_Operator(bpy.types.Operator, ImportHelper):
    """Load clothes from MHCLO file."""
    bl_idname = "mpfb.load_clothes"
    bl_label = "Load clothes from file"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.mhclo', options={'HIDDEN'})

    def invoke(self, context, event):
        blender_object = context.active_object
        return super().invoke(context, event)

    def _interpolate_weights(self, basemesh, clothes, rig, mhclo):

        clothes_weights = dict()
        for bone in rig.data.bones:
            clothes_weights[str(bone.name)] = []

        group_name_to_index = dict()
        group_index_to_name = dict()
        for group in basemesh.vertex_groups:
            if str(group.name) in clothes_weights:
                group_name_to_index[str(group.name)] = group.index
                group_index_to_name[int(group.index)] = str(group.name)

        for vert_number in range(len(mhclo.verts)):
            clothes_vert = mhclo.verts[vert_number]
            groups = dict()
            for v in range(3):
                human_vert = basemesh.data.vertices[clothes_vert["verts"][v]]
                assigned_weight = clothes_vert["weights"][v]
                for group in human_vert.groups:
                    idx = group.group
                    if idx in group_index_to_name:
                        if not idx in groups:
                            groups[idx] = []
                        groups[idx].append(group.weight * assigned_weight)
            for idx in groups.keys():
                average_weight = sum(groups[idx]) / len(groups[idx])
                if average_weight > 0.001:
                    group_name = group_index_to_name[int(idx)]
                    clothes_weights[group_name].append( [vert_number, average_weight] )

        for group_name in clothes_weights.keys():
            weights = clothes_weights[group_name]
            if len(weights) > 0:
                rotated = zip(*weights)
                indices = list(rotated)[0]
                new_vert_group = clothes.vertex_groups.new(name=str(group_name))
                new_vert_group.add(indices, 1.0, 'ADD')
                group_index = new_vert_group.index
                for weight_info in weights:
                    vertex_index = weight_info[0]
                    weight = weight_info[1]
                    for group in clothes.data.vertices[vertex_index].groups:
                        if int(group.group) == group_index:
                            group.weight = weight

    def execute(self, context):

        from mpfb.ui.loadclothes.loadclothespanel import LOAD_CLOTHES_PROPERTIES

        scene = context.scene

        object_type = LOAD_CLOTHES_PROPERTIES.get_value("object_type", entity_reference=scene)
        material_type = LOAD_CLOTHES_PROPERTIES.get_value("material_type", entity_reference=scene)
        fit_to_body = LOAD_CLOTHES_PROPERTIES.get_value("fit_to_body", entity_reference=scene)
        delete_group = LOAD_CLOTHES_PROPERTIES.get_value("delete_group", entity_reference=scene)
        set_up_rigging = LOAD_CLOTHES_PROPERTIES.get_value("set_up_rigging", entity_reference=scene)
        interpolate_weights = LOAD_CLOTHES_PROPERTIES.get_value("interpolate_weights", entity_reference=scene)

        blender_object = context.active_object

        rig = None
        basemesh = None

        if blender_object and not blender_object is None:
            if ObjectService.object_is_basemesh(blender_object):
                basemesh = blender_object
            else:
                basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Basemesh")

            rig = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Skeleton")

        if fit_to_body and basemesh is None:
            self.report({'ERROR'}, "Fit to body is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if delete_group and basemesh is None:
            self.report({'ERROR'}, "Set up delete group is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if interpolate_weights and basemesh is None:
            self.report({'ERROR'}, "interpolate weights is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if set_up_rigging and rig is None:
            self.report({'ERROR'}, "set up rigging is enabled, but could not find a rig to attach to")
            return {'FINISHED'}

        mhclo = Mhclo()
        mhclo.load(self.filepath)
        clothes = mhclo.load_mesh(context)

        if not clothes or clothes is None:
            self.report({'ERROR'}, "failed to import the clothes mesh")
            return {'FINISHED'}

        GeneralObjectProperties.set_value("object_type", object_type, entity_reference=clothes)
        bpy.ops.object.shade_smooth()

        if not material_type == "PRINCIPLED":
            MaterialService.delete_all_materials(clothes)

        if material_type == "MAKESKIN" and not mhclo.material is None:
            makeskin_material = MakeSkinMaterial()
            makeskin_material.populate_from_mhmat(mhclo.material)
            name = os.path.basename(mhclo.material)
            blender_material = MaterialService.create_empty_material(name, clothes)
            makeskin_material.apply_node_tree(blender_material)

        if fit_to_body:
            mhclo.update(basemesh)
            mhclo.set_scalings(context, basemesh)

        if set_up_rigging:
            clothes.location = (0.0, 0.0, 0.0)
            clothes.parent = rig
            modifier = clothes.modifiers.new("Armature", 'ARMATURE')
            modifier.object = rig

        self._interpolate_weights(basemesh, clothes, rig, mhclo)

        self.report({'INFO'}, "Clothes were loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Clothes_Operator)
