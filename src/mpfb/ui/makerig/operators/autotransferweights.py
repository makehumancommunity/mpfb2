"""Functionality for transfering weights from one mesh to another"""

from ....services import LogService
from ....services import ObjectService
from ....services import MeshService
from mpfb._classmanager import ClassManager
from mpfb.ui.mpfboperator import MpfbOperator
import bpy, math

_LOG = LogService.get_logger("makerig.autotransferweights")
_LOG.set_level(LogService.DEBUG)

MAX_DIST = 0.001

class MPFB_OT_Auto_Transfer_Weights_Operator(MpfbOperator):
    """Transfer weights for bones which occupy the same location"""
    bl_idname = "mpfb.auto_transfer_weights"
    bl_label = "Auto transfer weights"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        MpfbOperator.__init__(self, "makerig.autotransferweights")

    def hardened_execute(self, context):
        _LOG.enter()
        scene = context.scene

        armatures = ObjectService.get_selected_armature_objects()
        if len(armatures) != 2:
            self.report({"INFO"}, "Select 2 armatures")
            return {'CANCELED'}

        if context.active_object not in armatures:
            self.report({"INFO"}, "Armature must be active object")
            return {'CANCELED'}

        bm1 = ObjectService.find_object_of_type_amongst_nearest_relatives(armatures[0])
        bm2 = ObjectService.find_object_of_type_amongst_nearest_relatives(armatures[1])

        if bm1 is None or bm2 is None:
            self.report({"INFO"}, "Armature must have basemesh child")
            return {'CANCELED'}

        src_bm = None
        dst_bm = None

        src = context.active_object
        if src == armatures[0]:
            dst = armatures[1]
            src_bm = bm1
            dst_bm = bm2
        else:
            dst = armatures[0]
            src_bm = bm2
            dst_bm = bm1

        src_bones = {}
        dst_bones = {}

        for bone in src.data.bones:
            src_bones[bone.name] = [bone.head_local, bone.tail_local]

        for bone in dst.data.bones:
            dst_bones[bone.name] = [bone.head_local, bone.tail_local]

        bones_to_transfer = []

        for src_bone_name in src_bones.keys():
            src_loc = src_bones[src_bone_name]
            for dst_bone_name in dst_bones.keys():
                dst_loc = dst_bones[dst_bone_name]
                if math.dist(src_loc[0], dst_loc[0]) < MAX_DIST and math.dist(src_loc[1], dst_loc[1]) < MAX_DIST:
                    bones_to_transfer.append([src_bone_name, dst_bone_name])
                    break

        _LOG.debug("Bones to transfer", bones_to_transfer)

        done_bones = []

        for src_bone, dst_bone in bones_to_transfer:
            _LOG.debug("Transferring weights", (src_bone, dst_bone))
            weights = MeshService.find_vertices_in_vertex_group(src_bm, src_bone)
            _LOG.dump("Weights", weights)
            MeshService.create_vertex_group(dst_bm, dst_bone, weights, True)
            done_bones.append(dst_bone)

        missing_bones = []
        for bone in dst_bones.keys():
            if not bone in done_bones:
                missing_bones.append(bone)

        self.report({"INFO"}, "Transferred " + str(len(done_bones)) + " groups, leaving " + str(len(missing_bones)) + " unmatched. See console for details.")
        _LOG.info("Unmatched bones", missing_bones)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Auto_Transfer_Weights_Operator)
