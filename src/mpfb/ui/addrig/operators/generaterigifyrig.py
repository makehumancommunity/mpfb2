"""Operator for Generating a rigify rig."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
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
            return ObjectService.object_is_skeleton(context.active_object)
        return False

    def execute(self, context):
        scene = context.scene

        if not ObjectService.object_is_skeleton(context.active_object):
            self.report({'ERROR'}, "Must have armature object selected")
            return {'FINISHED'}

        from mpfb.ui.addrig.addrigpanel import ADD_RIG_PROPERTIES # pylint: disable=C0415

        armature_object = context.active_object
        delete_after_generate = ADD_RIG_PROPERTIES.get_value("delete_after_generate", entity_reference=scene)

        bpy.ops.pose.rigify_generate()
        rigify_object = context.active_object
        rigify_object.show_in_front = True

        _LOG.debug("rigify", rigify_object)

        for child in ObjectService.get_list_of_children(armature_object):

            child.parent = rigify_object

            for bone in armature_object.data.bones:
                name = bone.name
                if name in child.vertex_groups and not "teeth" in name:
                    vertex_group = child.vertex_groups.get(name)
                    vertex_group.name = "DEF-" + name

            for modifier in child.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.object = rigify_object

        if delete_after_generate:
            objs = bpy.data.objects
            objs.remove(objs[armature_object.name], do_unlink=True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        teethb = RigService.find_edit_bone_by_name("teeth.B", rigify_object)
        teethb.use_deform = True

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, "A rig was generated")
        return {'FINISHED'}



ClassManager.add_class(MPFB_OT_GenerateRigifyRigOperator)

