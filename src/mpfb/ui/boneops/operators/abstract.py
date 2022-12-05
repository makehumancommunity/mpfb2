"""Operator for recomputing bone head or tail position from strategy."""

import bpy
import typing
from mathutils import Vector

from mpfb.entities.rig import Rig
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService

from .. import BoneOpsArmatureProperties, BOP_PROPERTIES

_LOG = LogService.get_logger("boneops.abstract")

TBone = typing.TypeVar("TBone", bound=bpy.types.EditBone | bpy.types.Bone)


class AbstractBoneOperator(bpy.types.Operator):
    @staticmethod
    def is_developer_bone(context: bpy.types.Context):
        bone = context.edit_bone or context.bone
        return bone and BoneOpsArmatureProperties.get_value("developer_mode", entity_reference=bone.id_data)

    @staticmethod
    def is_developer_bone_edit(context: bpy.types.Context):
        return context.edit_bone and \
               context.active_object and \
               context.active_object.data == context.edit_bone.id_data and \
               AbstractBoneOperator.is_developer_bone(context)

    @staticmethod
    def get_bone_position(bone: TBone, is_tail: bool) -> Vector:
        if isinstance(bone, bpy.types.Bone):
            return bone.tail_local if is_tail else bone.head_local
        else:
            return bone.tail if is_tail else bone.head

    @staticmethod
    def find_linked_bones(context: bpy.types.Context, bone: TBone, is_tail: bool, *,
                          force=False, use_self=True, use_strategy=False, use_location=False
                          ) -> typing.Generator[tuple[TBone, bool], None, None]:
        assert use_strategy or use_location

        if not (force or BOP_PROPERTIES.get_value("keep_linked", entity_reference=context.scene)):
            if use_self:
                yield bone, is_tail
            return

        if isinstance(bone, bpy.types.EditBone):
            def get_pos(check_bone, check_tail):
                return check_bone.tail if check_tail else check_bone.head

            bone_list = bone.id_data.edit_bones
        else:
            def get_pos(check_bone, check_tail):
                return check_bone.tail_local if check_tail else check_bone.head_local

            bone_list = bone.id_data.bones

        info, _ = Rig.get_bone_end_strategy(bone, is_tail)
        pos = Vector(get_pos(bone, is_tail))  # copy value

        def check(check_bone, check_tail):
            if use_location:
                check_pos = get_pos(check_bone, check_tail)

                if (check_pos - pos).length < 1e-4:
                    return True

            if use_strategy and info:
                check_info, _ = Rig.get_bone_end_strategy(check_bone, check_tail)
                if check_info == info:
                    return True

        # Yield the first result after computing info and pos
        if use_self:
            yield bone, is_tail

        for iter_bone in bone_list:
            if iter_bone == bone:
                continue

            if check(iter_bone, False):
                yield iter_bone, False
            if check(iter_bone, True):
                yield iter_bone, True

    @staticmethod
    def unwrap_armature_object(armature_object):
        if isinstance(armature_object, (bpy.types.Bone, bpy.types.EditBone)):
            armature_object = armature_object.id_data

        if isinstance(armature_object, bpy.types.Armature):
            armature_object = ObjectService.find_by_data(armature_object)

        return armature_object

    def get_vertex_mesh(self, armature_object):
        _base_rig, _basemesh, direct_mesh = ObjectService.find_armature_context_objects(
            self.unwrap_armature_object(armature_object), operator=self)

        return direct_mesh

    def get_rig_entity(self, armature_object):
        return Rig.from_given_armature_context(
            self.unwrap_armature_object(armature_object), operator=self, empty=True)

    def switch_to_edit_mesh(self, context: bpy.types.Context, mesh_obj):
        edit_bone = context.edit_bone

        assert isinstance(context.space_data, bpy.types.SpaceProperties)

        if not context.space_data.use_pin_id:
            bpy.ops.ed.undo_push(message="Switch to mesh")

            bpy.ops.buttons.toggle_pin()

        if edit_bone:
            armature = ObjectService.find_by_data(edit_bone.id_data)

            assert armature

            ObjectService.activate_blender_object(armature, context=context)
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

            if armature.mode != "OBJECT":
                self.report({'ERROR'}, "Could not switch armature to object mode.")
                return False

        if context.active_object != mesh_obj:
            ObjectService.activate_blender_object(mesh_obj, context=context)

            if context.active_object != mesh_obj:
                self.report({'ERROR'}, "Could not select the mesh object.")
                return False

        if mesh_obj.mode != "EDIT":
            bpy.ops.object.mode_set(mode="EDIT", toggle=False)

            if mesh_obj.mode != "EDIT":
                self.report({'ERROR'}, "Could not switch mesh to edit mode.")
                return False

        return True

    def switch_to_edit_bone(self, context: bpy.types.Context, bone):
        armature = ObjectService.find_by_data(bone.id_data)
        bone_name = bone.name

        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

        ObjectService.activate_blender_object(armature, context=context)

        if context.active_object != armature:
            self.report({'ERROR'}, "Could not select the armature.")
            return False

        bpy.ops.object.mode_set(mode="EDIT", toggle=False)

        if armature.mode != "EDIT":
            self.report({'ERROR'}, "Could not switch the armature to edit mode.")
            return False

        assert isinstance(armature.data, bpy.types.Armature)

        armature.data.edit_bones.active = armature.data.edit_bones[bone_name]

        assert isinstance(context.space_data, bpy.types.SpaceProperties)

        if context.space_data.use_pin_id:
            bpy.ops.buttons.toggle_pin()

            bpy.ops.ed.undo_push(message="Switch from mesh")

        return True

    def set_cursor_pos(self, context, rig_entity, info):
        info_pos = rig_entity.get_best_location_from_strategy(info, use_default=False)

        if info_pos:
            context.scene.cursor.location = rig_entity.armature_object.matrix_world @ Vector(info_pos)
        else:
            self.report({'WARNING'}, "This strategy does not produce a valid position")
