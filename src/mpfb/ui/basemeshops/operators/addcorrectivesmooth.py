from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb._classmanager import ClassManager
import bpy


_LOG = LogService.get_logger("basemeshops.operators.addcorrectivesmooth")


class MPFB_OT_Add_Corrective_Smooth_Operator(bpy.types.Operator):
    """Add a corrective smooth modifier."""
    bl_idname = "mpfb.add_corrective_smooth"
    bl_label = "Add Corrective Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False

        objtype = ObjectService.get_object_type(context.object)

        if not objtype or context.object.type != "MESH":
            return False

        for modifier in context.object.modifiers:
            if modifier.type == 'CORRECTIVE_SMOOTH':
                return False

        return True

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'CANCELLED'}

        obj = context.object
        objtype = ObjectService.get_object_type(obj)

        if not objtype or obj.type != "MESH":
            self.report({'ERROR'}, "Can only add Corrective Smooth to MakeHuman meshes")
            return {'CANCELLED'}

        # Find the position where to add the modifier in the stack
        add_index = 0
        mutes = []

        for i, modifier in enumerate(obj.modifiers):
            if modifier.type == 'CORRECTIVE_SMOOTH':
                self.report({'ERROR'}, "Corrective smooth modifier already exists")
                return {'CANCELLED'}

            if modifier.type == 'ARMATURE':
                mutes.append(modifier.show_viewport)
                add_index = i + 1

        # Add the corrective smooth modifier
        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        smooth_modifier = obj.modifiers.new("Corrective Smooth", 'CORRECTIVE_SMOOTH')
        vg_name = "mhmask-no-smooth"

        if vg_name in obj.vertex_groups:
            smooth_modifier.vertex_group = vg_name
            smooth_modifier.invert_vertex_group = True

        while obj.modifiers.find(smooth_modifier.name) > add_index:
            bpy.ops.object.modifier_move_up({'object': object}, modifier=smooth_modifier.name)

        # Bake the neutral shape if the object has shape keys
        if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 1:
            # Disable armature deformation
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.show_viewport = False

            # Bind
            smooth_modifier.rest_source = "BIND"

            bpy.ops.object.correctivesmooth_bind({'object': object}, modifier=smooth_modifier.name)

            # Restore armature deformation
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.show_viewport = mutes.pop(0)

        self.report({'INFO'}, "Corrective smooth added")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Add_Corrective_Smooth_Operator)
