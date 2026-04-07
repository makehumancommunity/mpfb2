from .....services import LogService
from .....services import MaterialService
from .....services import ObjectService
from .....entities.rig import Rig
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext
import bpy, json, math
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("makerig.operators.loadrig")

class MPFB_OT_Load_Rig_Operator(MpfbOperator, ImportHelper):
    """Load rig from definition in json"""
    bl_idname = "mpfb.load_rig"
    bl_label = "Load rig"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.mpfbskel'

    def get_logger(self):
        return _LOG

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.active_object is None:
            return False

        from ...makerig import MakeRigProperties
        rig_subrig = MakeRigProperties.get_value("rig_subrig", entity_reference=context.scene)

        if rig_subrig:
            if not ObjectService.object_is_any_mesh(context.active_object):
                return False

            if ObjectService.object_is_basemesh(context.active_object):
                return False

            skeleton = ObjectService.find_object_of_type_amongst_nearest_relatives(
                context.active_object, "Skeleton", only_parents=True)

            if not skeleton:
                return False

            return True

        else:
            return ObjectService.object_is_basemesh(context.active_object)

    def hardened_execute(self, context):
        _LOG.enter()

        from ...makerig import MakeRigProperties
        ctx = MpfbContext(context=context, scene_properties=MakeRigProperties)

        mesh = context.active_object
        skeleton = None

        if ctx.rig_subrig:
            if mesh is None or mesh.type != "MESH" or ObjectService.object_is_basemesh(mesh):
                self.report({'ERROR'}, "Must have a mesh asset as active object")
                return {'CANCELLED'}

            skeleton = ObjectService.find_object_of_type_amongst_nearest_relatives(
                context.active_object, "Skeleton", only_parents=True)

            if not skeleton:
                self.report({'ERROR'}, "Could not find the main skeleton among the parents.")
                return {'CANCELLED'}

            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(
                skeleton, "Basemesh", only_children=True)

            if not basemesh:
                self.report({'ERROR'}, "Could not find the base mesh among children of the main skeleton.")
                return {'CANCELLED'}

        else:
            if mesh is None or not ObjectService.object_is_basemesh(mesh):
                self.report({'ERROR'}, "Must have basemesh as active object")
                return {'CANCELLED'}

            basemesh = mesh

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        if ctx.rig_subrig:
            parent_rig = Rig.from_given_basemesh_and_armature(basemesh, skeleton, fast_positions=True)

            rig = Rig.from_json_file_and_basemesh(absolute_file_path, mesh, parent=parent_rig)
        else:
            rig = Rig.from_json_file_and_basemesh(absolute_file_path, basemesh)

        armature_object = rig.create_armature_and_fit_to_basemesh(for_developer=True)

        if ctx.rig_parent:
            mesh.parent = armature_object

            if ctx.rig_subrig:
                armature_object.parent = skeleton

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Rig_Operator)
