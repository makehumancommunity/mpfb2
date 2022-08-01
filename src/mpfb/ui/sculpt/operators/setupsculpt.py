from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb._classmanager import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("sculpt.operators.setupsculpt")

class MPFB_OT_Setup_Sculpt_Operator(bpy.types.Operator):
    """Bake all shape keys into a final mesh and optionally perform other operations suitable for starting a sculpt project. WARNING: You will no longer be able to adjust targets after doing this."""
    bl_idname = "mpfb.setup_sculpt"
    bl_label = "Set up mesh for sculpt"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False

        objtype = GeneralObjectProperties.get_value("object_type", entity_reference=context.object)

        if not objtype or objtype == "Skeleton":
            return

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
            _LOG.dump("group name", group.name)
            if vgroup_name in group.name:
                group_idx = group.index
        _LOG.dump("group index", group_idx)

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

    def _clear_subdiv(self, context, obj):
        for modifier in obj.modifiers:
            if modifier.type == 'SUBSURF':
                obj.modifiers.remove(modifier)

    def _handle_armature(self, context, obj, apply_armature, delete_if_not_apply=True):
        if not apply_armature and not delete_if_not_apply:
            return
        if apply_armature:
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    bpy.ops.object.modifier_apply( modifier = modifier.name )
        else:
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    obj.modifiers.remove(modifier)

    def _handle_bm(self, context, basemesh, delete_helpers):
        TargetService.bake_targets(basemesh)
        if delete_helpers:
            for modifier in basemesh.modifiers:
                if modifier.type == 'MASK' and modifier.vertex_group == 'body':
                    basemesh.modifiers.remove(modifier)
            self._delete_vertex_group(context, basemesh, "HelperGeometry")
            self._delete_vertex_group(context, basemesh, "JointCubes")

    def _create_clean_copies(self, context, obj, apply_armature, delete_helpers, remove_delete, create_source_copy=False):
        obj.select_set(state=True)
        context.view_layer.objects.active = obj

        bpy.ops.object.duplicate(linked=False)

        objtype = GeneralObjectProperties.get_value("object_type", entity_reference=context.object)

        dest = context.object
        dest.name = "Object to bake to (select second when baking)"
        dest.parent = None
        _LOG.debug("Dest object", dest)

        if objtype == "Basemesh":
            self._handle_bm(context, dest, delete_helpers)

        self._handle_armature(context, dest, apply_armature)

        if remove_delete:
            for modifier in dest.modifiers:
                if modifier.type == 'MASK' and modifier.vertex_group != 'body':
                    dest.modifiers.remove(modifier)

        self._clear_subdiv(context, dest)

        MaterialService.delete_all_materials(dest)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        _LOG.debug("context.object", context.object)

        obj.select_set(state=False)
        dest.select_set(state=True)
        context.view_layer.objects.active = dest

        if not create_source_copy:
            return (None, dest)

        _LOG.debug("context.object", context.object)

        bpy.ops.object.duplicate(linked=False)

        _LOG.debug("context.object", context.object)

        source = context.object
        source.name = "Object to sculpt (select first when baking)"
        source.parent = None
        _LOG.debug("Source object", source)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return (source, dest)

    def _setup_materials(self, context, dest, normal_material, resolution):
        if normal_material:
            MaterialService.delete_all_materials(dest)
            material = MaterialService.create_empty_material('Material for baking normal map', dest)
            material.diffuse_color = MaterialService.get_skin_diffuse_color()
            nodes = material.node_tree
            principled = NodeService.find_first_node_by_type_name(nodes, 'ShaderNodeBsdfPrincipled')
            principled.inputs['Base Color'].default_value = MaterialService.get_skin_diffuse_color()
            imgtex = NodeService.create_image_texture_node(nodes, xpos=-700)
            side = int(resolution)
            bpy.ops.image.new(name='Sculpt normal map', width=side, height=side)
            imgtex.image = bpy.data.images['Sculpt normal map']

    def _setup_multires(self, context, obj, setup_multires, subdivisions, multires_first):
        obj.select_set(state=True)
        context.view_layer.objects.active = obj
        if setup_multires:
            self._clear_subdiv(context, obj)
            modifier = obj.modifiers.new('Sculpt multires', 'MULTIRES')
            if multires_first:
                while obj.modifiers.find(modifier.name) != 0:
                    bpy.ops.object.modifier_move_up({'object': obj}, modifier=modifier.name)

            if subdivisions > 0:
                for n in range(subdivisions):
                    bpy.ops.object.multires_subdivide(modifier="Sculpt multires")

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'FINISHED'}

        obj = context.object

        objtype = GeneralObjectProperties.get_value("object_type", entity_reference=context.object)

        if not objtype or objtype == "Skeleton":
            self.report({'ERROR'}, "Can only prepare makehuman type meshes")
            return {'FINISHED'}

        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        from mpfb.ui.sculpt.sculptpanel import SCULPT_PROPERTIES

        adjust_settings = SCULPT_PROPERTIES.get_value("adjust_settings", entity_reference=context.scene)
        apply_armature = SCULPT_PROPERTIES.get_value("apply_armature", entity_reference=context.scene)
        delete_helpers = SCULPT_PROPERTIES.get_value("delete_helpers", entity_reference=context.scene)
        hide_origin = SCULPT_PROPERTIES.get_value("hide_origin", entity_reference=context.scene)
        hide_related = SCULPT_PROPERTIES.get_value("hide_related", entity_reference=context.scene)
        enter_sculpt = SCULPT_PROPERTIES.get_value("enter_sculpt", entity_reference=context.scene)
        multires_first = SCULPT_PROPERTIES.get_value("multires_first", entity_reference=context.scene)
        normal_material = SCULPT_PROPERTIES.get_value("normal_material", entity_reference=context.scene)
        remove_delete = SCULPT_PROPERTIES.get_value("remove_delete", entity_reference=context.scene)
        resolution = SCULPT_PROPERTIES.get_value("resolution", entity_reference=context.scene)
        sculpt_strategy = SCULPT_PROPERTIES.get_value("sculpt_strategy", entity_reference=context.scene)
        setup_multires = SCULPT_PROPERTIES.get_value("setup_multires", entity_reference=context.scene)
        subdivisions = SCULPT_PROPERTIES.get_value("subdivisions", entity_reference=context.scene)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        _LOG.debug("Selected object", obj)

        dest = None
        source = None

        if sculpt_strategy in ["DESTCOPY", "SOURCEDESTCOPY"]:

            source_copy = sculpt_strategy == "SOURCEDESTCOPY"
            _LOG.debug("source_copy", source_copy)
            (source, dest) = self._create_clean_copies(context, obj, apply_armature, delete_helpers, remove_delete, create_source_copy=source_copy)
            self._setup_materials(context, dest, normal_material, resolution)

            if not source:
                source = obj
                self._handle_bm(context, source, delete_helpers)
                self._handle_armature(context, source, apply_armature)

                if remove_delete:
                    for modifier in source.modifiers:
                        if modifier.type == 'MASK' and modifier.vertex_group != 'body':
                            source.modifiers.remove(modifier)

            _LOG.debug("source, dest, obj", (source, dest, obj))

            self._clear_subdiv(context, source)
            self._setup_multires(context, source, setup_multires, subdivisions, multires_first)
            self._setup_multires(context, dest, setup_multires, subdivisions, multires_first)

            dest.select_set(state=False)
            obj.select_set(state=False)
            source.select_set(state=True)
            context.view_layer.objects.active = source

            dest.hide_viewport = True

            if source_copy and hide_origin:
                parent = obj
                if obj.parent:
                    parent = obj.parent

                for child in ObjectService.get_list_of_children(parent):
                    child.hide_viewport = True

                parent.hide_viewport = True

            _LOG.debug("source_copy, obj, hide_related", (source_copy, obj, hide_related))

            if not source_copy and hide_related:
                parent = obj
                if obj.parent:
                    parent = obj.parent

                parent.hide_viewport = False

                for child in ObjectService.get_list_of_children(parent):
                    child.hide_viewport = True
                    _LOG.debug("Hiding", child)

                source.hide_viewport = False
                source.select_set(state=True)
                context.view_layer.objects.active = source

        if sculpt_strategy == "ORIGIN":
            if hide_related:
                parent = obj
                if obj.parent:
                    parent = obj.parent

                parent.hide_viewport = False

                for child in ObjectService.get_list_of_children(parent):
                    child.hide_viewport = True
                    _LOG.debug("Hiding", child)

            obj.hide_viewport = False
            obj.select_set(state=True)
            context.view_layer.objects.active = obj

            self._handle_bm(context, obj, delete_helpers)
            self._setup_multires(context, obj, setup_multires, subdivisions, multires_first)

        if sculpt_strategy != "ORIGIN" and adjust_settings:
            scene = context.scene
            scene.cycles.samples = 8
            scene.cycles.adaptive_min_samples = 1
            scene.cycles.use_denoising = False
            scene.cycles.bake_type = 'NORMAL'
            scene.render.use_bake_multires = False
            scene.render.bake.use_selected_to_active = True
            scene.render.bake.cage_extrusion = 0.01
            scene.render.bake.max_ray_distance = 0.1

        if enter_sculpt:
            bpy.ops.object.mode_set(mode='SCULPT', toggle=False)

        if sculpt_strategy == "DESTCOPY" and source and MaterialService.has_materials(source):
            self.report({'WARNING'}, "Setup has finished, but note that the sculpt object still has materials. This may cause artifacts when baking a normal map.")
        else:
            self.report({'INFO'}, "Setup finished")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Setup_Sculpt_Operator)
