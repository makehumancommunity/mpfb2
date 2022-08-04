"""Operator for loading an alternative material"""

import bpy
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.services.materialservice import MaterialService
from mpfb.services.assetservice import AssetService
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibraryskin")

class MPFB_OT_Load_Library_Material_Operator(bpy.types.Operator):
    """Replace the current material with the selected alternative material"""
    bl_idname = "mpfb.load_library_material"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        from mpfb.ui.assetlibrary.alternativematerialpanel import ALTMAT_PROPERTIES # pylint: disable=C0415

        scene = context.scene
        obj = context.object

        selected_material = ALTMAT_PROPERTIES.get_value("available_materials", entity_reference=scene)

        if not selected_material or selected_material == "DEFAULT":
            pass
        else:
            if MaterialService.has_materials(obj):
                while len(obj.data.materials) > 0:
                    obj.data.materials.pop(index=0)

            material = MaterialService.create_empty_material("makeskinmaterial", obj)

            mhmat = MakeSkinMaterial()
            mhmat.populate_from_mhmat(selected_material)
            mhmat.apply_node_tree(material)

            object_type = ObjectService.get_object_type(obj)

            atype = str(object_type).lower().capitalize()
            colors = MaterialService.get_diffuse_colors()
            _LOG.dump("Colors, atype, exists", (colors, atype, atype in colors))
            color = (0.8, 0.8, 0.8, 1.0)

            if atype in colors:
                color = colors[atype]

            material.diffuse_color = color

            # TODO: Hitta full path från mhclo attribut på objekt. Skicka in som parameter två
            fragment = AssetService.path_to_fragment(selected_material, relative_to_fragment=False, asset_subdir=str(object_type).lower())
            _LOG.debug("Fragment", fragment)

            from mpfb.entities.objectproperties import GeneralObjectProperties
            GeneralObjectProperties.set_value("alternative_material", fragment, entity_reference=obj)

        self.report({'INFO'}, "Material was loaded: " + selected_material)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Material_Operator)
