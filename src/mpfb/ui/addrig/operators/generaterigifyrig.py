"""Operator for Generating a rigify rig."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb.services.systemservice import SystemService
from mpfb import ClassManager

_LOG = LogService.get_logger("addrig.generate_rigify_rig")

class MPFB_OT_GenerateRigifyRigOperator(bpy.types.Operator):
    """Generate a rigify rig from a meta-rig"""

    bl_idname = "mpfb.generate_rigify_rig"
    bl_label = "Generate"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            if not ObjectService.object_is_skeleton(context.active_object):
                return False
            rig_type = RigService.identify_rig(context.active_object)
            return rig_type.startswith("rigify.")
        return False

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
        scene = context.scene

        if not ObjectService.object_is_skeleton(context.active_object):
            self.report({'ERROR'}, "Must have armature object selected")
            return {'FINISHED'}

        if not SystemService.check_for_rigify():
            self.report({'ERROR'}, "The rigify addon isn't enabled. You need to enable it under preferences.")
            return {'FINISHED'}

        from mpfb.ui.addrig.addrigpanel import ADD_RIG_PROPERTIES # pylint: disable=C0415

        armature_object = context.active_object
        delete_after_generate = ADD_RIG_PROPERTIES.get_value("delete_after_generate", entity_reference=scene)
        teeth = ADD_RIG_PROPERTIES.get_value("teeth", entity_reference=scene)

        explicit_name = str(ADD_RIG_PROPERTIES.get_value("name", entity_reference=scene)).strip()

        name = armature_object.name

        if explicit_name:
            name = explicit_name

        if name:
            # Yes, the following logic is excessively messy, but rigify handles naming differently if the original
            # name contains the word "metarig"
            target_name = name
            if target_name.endswith(".metarig"):
                target_name = name.replace(".metarig", ".rig")
            if ObjectService.object_name_exists(target_name) or ObjectService.object_name_exists("RIG-" + target_name):
                target_name = ObjectService.ensure_unique_name("RIG-" + name)
                target_name = target_name.replace("RIG-", "")
            else:
                target_name = name
            _LOG.debug("Setting name", target_name)
            if hasattr(armature_object.data, 'rigify_rig_basename'):
                armature_object.data.rigify_rig_basename = target_name
            else:
                armature_object.name = target_name

        # Switch to the new face rig
        if bpy.ops.pose.rigify_upgrade_face.poll():
            bpy.ops.pose.rigify_upgrade_face()

        bpy.ops.pose.rigify_generate()
        rigify_object = context.active_object
        rigify_object.show_in_front = True

        _LOG.debug("rigify", rigify_object)

        for child in ObjectService.get_list_of_children(armature_object):

            child.parent = rigify_object

            for bone in armature_object.data.bones:
                name = bone.name
                if not name.startswith("DEF-") and name in child.vertex_groups:
                    vertex_group = child.vertex_groups.get(name)
                    vertex_group.name = "DEF-" + name

            for modifier in child.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.object = rigify_object

        if delete_after_generate:
            objs = bpy.data.objects
            objs.remove(objs[armature_object.name], do_unlink=True)

        _LOG.debug("Teeth strategy", teeth)

        if teeth == "RIG":
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            teethb = RigService.find_edit_bone_by_name("teeth.B", rigify_object)
            teethb.use_deform = True
            teethb.name = "DEF-teeth.B"

        if teeth == "SPLIT":
            upper_teeth = ObjectService.find_object_of_type_amongst_nearest_relatives(rigify_object, "Teeth")
            _LOG.debug("Teeth object", upper_teeth)
            if upper_teeth:
                lower_teeth = upper_teeth.copy()
                lower_teeth.data = upper_teeth.data.copy()
                lower_teeth.animation_data_clear()
                lower_teeth.name = upper_teeth.name + ".lower"
                context.collection.objects.link(lower_teeth)

                self._delete_vertex_group(context, lower_teeth, "teeth.T")
                self._delete_vertex_group(context, upper_teeth, "teeth.B")

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.select_all(action='DESELECT')

                lower_teeth.parent_bone = "teeth.B"
                lower_teeth.parent_type = 'BONE'
                lower_teeth.matrix_world.translation = (0.0, 0.0, 0.0)

        rigify_object.select_set(True)
        context.view_layer.objects.active = rigify_object
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        from mpfb.entities.objectproperties import GeneralObjectProperties
        GeneralObjectProperties.set_value("object_type", "Skeleton", entity_reference=rigify_object)

        self.report({'INFO'}, "A rig was generated")
        return {'FINISHED'}



ClassManager.add_class(MPFB_OT_GenerateRigifyRigOperator)

