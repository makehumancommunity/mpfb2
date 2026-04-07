"""Operator for creating a template MakeSkin material."""

import bpy
from .....services import LogService
from .....services import MaterialService
from .....entities.material.makeskinmaterial import MakeSkinMaterial
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext

_LOG = LogService.get_logger("makeskin.creatematerial")

@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_CreateMaterialOperator(MpfbOperator):
    """Create template material"""
    bl_idname = "mpfb.create_makeskin_material"
    bl_label = "Create material"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        from ...makeskin.makeskinpanel import MAKESKIN_PROPERTIES  # pylint: disable=C0415
        from ...makeskin import MakeSkinObjectProperties  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=MAKESKIN_PROPERTIES, object_properties=MakeSkinObjectProperties)

        if MaterialService.has_materials(ctx.active_object):
            MaterialService.delete_all_materials(ctx.active_object)

        name = ctx.name or "MakeSkinMaterial"

        if ctx.create_specularmap and ctx.create_roughnessmap:
            self.report({'ERROR'}, "Cannot set specular and roughness maps at the same time.")
            return {'CANCELLED'}

        MakeSkinMaterial.create_makeskin_template_material(ctx.active_object, ctx.scene, name)

        self.report({'INFO'}, "Material was created")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_CreateMaterialOperator)
