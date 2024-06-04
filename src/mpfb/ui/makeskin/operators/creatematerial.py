"""Operator for creating a template MakeSkin material."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.ui.makeskin.makeskinpanel import MAKESKIN_PROPERTIES
from mpfb import ClassManager

_LOG = LogService.get_logger("makeskin.creatematerial")


class MPFB_OT_CreateMaterialOperator(bpy.types.Operator):
    """Create template material"""
    bl_idname = "mpfb.create_makeskin_material"
    bl_label = "Create material"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return context.active_object.type == "MESH"
        return False

    def execute(self, context):

        blender_object = context.active_object
        scene = context.scene

        from mpfb.ui.makeskin.makeskinpanel import MAKESKIN_PROPERTIES  # pylint: disable=C0415
        from mpfb.ui.makeskin import MakeSkinObjectProperties  # pylint: disable=C0415

        if MaterialService.has_materials(blender_object):
            MaterialService.delete_all_materials(blender_object)

        name = MakeSkinObjectProperties.get_value("name", entity_reference=blender_object)
        if not name:
            name = "MakeSkinMaterial"

        create_specularmap = MAKESKIN_PROPERTIES.get_value("create_specularmap", entity_reference=scene)
        create_roughnessmap = MAKESKIN_PROPERTIES.get_value("create_roughnessmap", entity_reference=scene)

        if create_specularmap and create_roughnessmap:
            self.report({'ERROR'}, "Cannot set specular and roughness maps at the same time.")
            return {'CANCELLED'}

        MakeSkinMaterial.create_makeskin_template_material(blender_object, scene, name)

        self.report({'INFO'}, "Material was created")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateMaterialOperator)
