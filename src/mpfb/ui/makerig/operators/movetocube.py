"""Functionality for adjusting location of edit bone"""

from ....services import LogService
from ....services import ObjectService
from mpfb._classmanager import ClassManager
from mpfb.ui.mpfboperator import MpfbOperator
import bpy, math

_LOG = LogService.get_logger("makerig.movetocube")
_LOG.set_level(LogService.DEBUG)

_CUBE_CENTER_CACHE = {}

class MPFB_OT_Move_To_Cube_Operator(MpfbOperator):
    """Move head and tail to center of joint cubes"""
    bl_idname = "mpfb.move_bone_to_cube"
    bl_label = "Move to cubes"
    bl_options = {'REGISTER'}

    def __init__(self):
        MpfbOperator.__init__(self, "makerig.movetocube")

    def _move(self, item, move_to, basemesh):
        _LOG.debug("Location before", item)
        _LOG.debug("Move to cube", move_to)
        if move_to not in ["NONE", "CLOSEST"]:
            dest = _CUBE_CENTER_CACHE[basemesh.name][move_to]
            item[0] = dest[0]
            item[1] = dest[1]
            item[2] = dest[2]
        if move_to == "CLOSEST":
            least_distance = 100.0
            least_distance_name = None
            for key in _CUBE_CENTER_CACHE[basemesh.name].keys():
                target = _CUBE_CENTER_CACHE[basemesh.name][key]
                distance_to_item = math.sqrt((target[0] - item[0])**2 + (target[1] - item[1])**2 + (target[2] - item[2])**2)
                if distance_to_item < least_distance:
                    least_distance = distance_to_item
                    least_distance_name = key
            dest = _CUBE_CENTER_CACHE[basemesh.name][least_distance_name]
            item[0] = dest[0]
            item[1] = dest[1]
            item[2] = dest[2]
        _LOG.debug("Location after", item)

    def hardened_execute(self, context):
        _LOG.enter()

        scene = context.scene

        basemesh = None
        armature = None

        if not context.object or context.object.type != "ARMATURE":
            self.report({"ERROR"}, "Need armature as active")
            return {'CANCELED'}

        armature = context.object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature, "Basemesh")

        if not basemesh:
            selected = ObjectService.get_selected_objects(exclude_non_mh_objects=True, exclude_armature_objects=True)
            for obj in selected:
                if ObjectService.object_is_basemesh(obj):
                    basemesh = obj

        if not basemesh:
            self.report({"ERROR"}, "Select basemesh too")
            return {'CANCELED'}

        if armature.mode != "EDIT":
            self.report({"ERROR"}, "Edit mode only")
            return {'CANCELED'}

        if len(context.selected_bones) != 1:
            self.report({"ERROR"}, "Select exactly one bone")
            return {'CANCELED'}

        if basemesh.name not in _CUBE_CENTER_CACHE:
            _LOG.debug("Building cache")
            _CUBE_CENTER_CACHE[basemesh.name] = {}
            for key in ObjectService.get_base_mesh_vertex_group_definition().keys():
                if "joint-" in key:
                    relevant_verts = ObjectService.get_base_mesh_vertex_group_definition()[key]
                    _LOG.debug("Relevant verts", (key, relevant_verts))
                    vertex_mean_location = [0.0, 0.0, 0.0]
                    for vert in basemesh.data.vertices:
                        if vert.index in relevant_verts:
                            vertex_mean_location[0] += vert.co.x
                            vertex_mean_location[1] += vert.co.y
                            vertex_mean_location[2] += vert.co.z
                    vertex_mean_location[0] /= len(relevant_verts)
                    vertex_mean_location[1] /= len(relevant_verts)
                    vertex_mean_location[2] /= len(relevant_verts)
                    _CUBE_CENTER_CACHE[basemesh.name][key] = vertex_mean_location

        selected_bone = context.selected_bones[0]

        head = selected_bone.head
        tail = selected_bone.tail

        _LOG.debug("Head, tail", (head, tail))

        from mpfb.ui.makerig import MakeRigProperties
        head_cube = MakeRigProperties.get_value("head_cube", entity_reference=scene)
        tail_cube = MakeRigProperties.get_value("tail_cube", entity_reference=scene)

        self._move(head, head_cube, basemesh)
        self._move(tail, tail_cube, basemesh)

        self.report({"INFO"}, "Done")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Move_To_Cube_Operator)
