from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService
from mpfb._classmanager import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("sculpt.operators.setupsculpt")

class MPFB_OT_Setup_Sculpt_Operator(bpy.types.Operator):
    """Bake all shape keys into a final mesh and optionally perform other operations suitable for setting up a sculpt project"""
    bl_idname = "mpfb.setup_sculpt"
    bl_label = "Bake mesh for sculpt"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False
        return True

    def _delete_vertex_group(self, context, blender_object, vgroup_name):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = blender_object
        blender_object.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        group_idx = None
        for group in blender_object.vertex_groups:
            _LOG.debug("group name", group.name)
            if vgroup_name in group.name:
                group_idx = group.index
        _LOG.debug("group index", group_idx)

        for vertex in blender_object.data.vertices:
            vertex.select = False
            for group in vertex.groups:
                if group.group == group_idx:
                    vertex.select = True
            _LOG.dump("Vertex index, selected", (vertex.index, vertex.select))

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        blender_object.select_set(False)

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'FINISHED'}

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, 'Basemesh')


        if basemesh is None:
            self.report({'ERROR'}, "Could not find base mesh")
            return {'FINISHED'}

        context.view_layer.objects.active = basemesh

        from mpfb.ui.sculpt.sculptpanel import SCULPT_PROPERTIES
        delete_helpers = SCULPT_PROPERTIES.get_value("delete_helpers", entity_reference=context.scene)
        delete_proxies = SCULPT_PROPERTIES.get_value("delete_proxies", entity_reference=context.scene)
        apply_armature = SCULPT_PROPERTIES.get_value("apply_armature", entity_reference=context.scene)
        enter_sculpt = SCULPT_PROPERTIES.get_value("enter_sculpt", entity_reference=context.scene)
        normal_material = SCULPT_PROPERTIES.get_value("normal_material", entity_reference=context.scene)
        remove_delete = SCULPT_PROPERTIES.get_value("remove_delete", entity_reference=context.scene)
        setup_multires = SCULPT_PROPERTIES.get_value("setup_multires", entity_reference=context.scene)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        TargetService.bake_targets(basemesh)

        if delete_helpers:
            for modifier in basemesh.modifiers:
                if modifier.type == 'MASK' and modifier.vertex_group == 'body':
                    basemesh.modifiers.remove(modifier)
            self._delete_vertex_group(context, basemesh, "HelperGeometry")
            self._delete_vertex_group(context, basemesh, "JointCubes")

        if remove_delete:
            for modifier in basemesh.modifiers:
                if modifier.type == 'MASK':
                    basemesh.modifiers.remove(modifier)

        if delete_proxies:
            parent = basemesh
            if basemesh.parent:
                parent = basemesh.parent
            children = ObjectService.get_list_of_children(parent)
            for child in children:
                if child != basemesh and child.type != "ARMATURE":
                    bpy.data.objects.remove(child, do_unlink=True)

        if apply_armature:
            for modifier in basemesh.modifiers:
                if modifier.type == 'ARMATURE':
                    bpy.ops.object.modifier_apply( modifier = modifier.name )
            armature = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, 'Skeleton')
            if armature:
                bpy.data.objects.remove(armature, do_unlink=True)

        if setup_multires:
            for modifier in basemesh.modifiers:
                if modifier.type == 'SUBSURF':
                    basemesh.modifiers.remove(modifier)
            modifier = basemesh.modifiers.new('Sculpt multires', 'MULTIRES')
            bpy.ops.object.multires_subdivide(modifier="Sculpt multires")
            bpy.ops.object.multires_subdivide(modifier="Sculpt multires")
            modifier.levels = 0

        if normal_material:
            MaterialService.delete_all_materials(basemesh)
            material = MaterialService.create_empty_material('Material for baking normal map', basemesh)
            material.diffuse_color = MaterialService.get_skin_diffuse_color()
            nodes = material.node_tree
            principled = NodeService.find_first_node_by_type_name(nodes, 'ShaderNodeBsdfPrincipled')
            principled.inputs['Base Color'].default_value = MaterialService.get_skin_diffuse_color()
            imgtex = NodeService.create_image_texture_node(nodes, xpos=-700)
            bpy.ops.image.new(name='Sculpt normal map', width=8192, height=8192)
            imgtex.image = bpy.data.images['Sculpt normal map']

        if enter_sculpt:
            bpy.ops.object.mode_set(mode='SCULPT', toggle=False)

        self.report({'INFO'}, "Baked finished")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Setup_Sculpt_Operator)
