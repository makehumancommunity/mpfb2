"""Operator for Generating a rigify rig."""

import bpy
from ....services import LogService
from ....services import ObjectService
from ....entities.rigging.rigifyhelpers.rigifyhelpers import RigifyHelpers
from ....services import RigService
from ....services import SystemService
from .... import ClassManager

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

    def execute(self, context):
        scene = context.scene

        if not ObjectService.object_is_any_skeleton(context.active_object):
            self.report({'ERROR'}, "Must have armature object selected")
            return {'FINISHED'}

        if not SystemService.check_for_rigify():
            self.report({'ERROR'}, "The rigify addon isn't enabled. You need to enable it under preferences.")
            return {'FINISHED'}

        from ...addrig.addrigpanel import ADD_RIG_PROPERTIES  # pylint: disable=C0415

        armature_object = context.active_object
        delete_after_generate = ADD_RIG_PROPERTIES.get_value("delete_after_generate", entity_reference=scene)

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

        rigify_object.select_set(True)
        context.view_layer.objects.active = rigify_object
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        from mpfb.entities.objectproperties import GeneralObjectProperties

        object_type = ObjectService.get_object_type(armature_object)
        GeneralObjectProperties.set_value("object_type", object_type, entity_reference=rigify_object)

        self.report({'INFO'}, "A rig was generated")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_GenerateRigifyRigOperator)

