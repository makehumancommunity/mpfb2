"""Operator for Generating a rigify rig."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigifyhelpers.rigifyhelpers import RigifyHelpers
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
            if not ObjectService.object_is_any_skeleton(context.active_object):
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

        if not ObjectService.object_is_any_skeleton(context.active_object):
            self.report({'ERROR'}, "Must have armature object selected")
            return {'FINISHED'}

        if not SystemService.check_for_rigify():
            self.report({'ERROR'}, "The rigify addon isn't enabled. You need to enable it under preferences.")
            return {'FINISHED'}

        from mpfb.ui.addrig.addrigpanel import ADD_RIG_PROPERTIES # pylint: disable=C0415

        armature_object = context.active_object
        delete_after_generate = ADD_RIG_PROPERTIES.get_value("delete_after_generate", entity_reference=scene)

        # Sub-rigs should not have any teeth, so ignore option in that case
        if ObjectService.object_is_skeleton(armature_object):
            teeth = ADD_RIG_PROPERTIES.get_value("teeth", entity_reference=scene)
        else:
            teeth = "KEEP"

        explicit_name = str(ADD_RIG_PROPERTIES.get_value("name", entity_reference=scene)).strip()

        # If the metarig is named incorrectly (e.g. in case of sub-rigs), rename it
        if armature_object.name.endswith(".rig"):
            armature_object.name = armature_object.data.name = armature_object.name.replace(".rig", ".metarig")

        if explicit_name:
            if hasattr(armature_object.data, 'rigify_rig_basename'):
                armature_object.data.rigify_rig_basename = explicit_name
            else:
                armature_object.name = explicit_name.replace("rig", "metarig")

        elif hasattr(armature_object.data, 'rigify_generate_mode'):
            # Try to preserve fix for issue #17 in legacy rigify, which has issues if the object exists.
            name = armature_object.name.replace("metarig", "rig")

            armature_object.data.rigify_rig_basename = ObjectService.ensure_unique_name(name)

        # Switch to the new face rig
        if bpy.ops.pose.rigify_upgrade_face.poll():
            bpy.ops.pose.rigify_upgrade_face()

        bpy.ops.pose.rigify_generate()

        rigify_object = context.active_object
        rigify_object.show_in_front = True

        rigify_object.parent = armature_object.parent

        _LOG.debug("rigify", rigify_object)

        RigifyHelpers.adjust_children_for_rigify(rigify_object, armature_object)

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

        object_type = ObjectService.get_object_type(armature_object)
        GeneralObjectProperties.set_value("object_type", object_type, entity_reference=rigify_object)

        self.report({'INFO'}, "A rig was generated")
        return {'FINISHED'}



ClassManager.add_class(MPFB_OT_GenerateRigifyRigOperator)

