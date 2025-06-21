"""Operator for loading an alternative material"""

import bpy, os
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import HumanService
from ....services import MaterialService
from ....services import AssetService
from ....entities.material.makeskinmaterial import MakeSkinMaterial
from .... import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibrarymaterial")


class MPFB_OT_Load_Library_Material_Operator(bpy.types.Operator):
    """Replace the current material with the selected alternative material"""
    bl_idname = "mpfb.load_library_material"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        from ...assetlibrary.alternativematerialpanel import ALTMAT_PROPERTIES  # pylint: disable=C0415

        scene = context.scene
        obj = context.object

        selected_material = ALTMAT_PROPERTIES.get_value("available_materials", entity_reference=scene)

        if not selected_material or selected_material == "DEFAULT":
            pass
        else:
            asset_type = ObjectService.get_object_type(context.object)
            from ....entities.objectproperties import GeneralObjectProperties
            source = GeneralObjectProperties.get_value("asset_source", entity_reference=context.object)
            altmats = AssetService.alternative_materials_for_asset(source, str(asset_type).lower())
            found_material = None
            for mat in altmats:
                bn = str(os.path.basename(mat))
                if bn == selected_material:
                    found_material = mat
                    break
            if found_material is None:
                self.report({'ERROR'}, "Could not find full path to alternative material: " + selected_material)
                return {'CANCELED'}

            if MaterialService.has_materials(obj):
                while len(obj.data.materials) > 0:
                    obj.data.materials.pop(index=0)

            material = MaterialService.create_empty_material("makeskinmaterial", obj)

            mhmat = MakeSkinMaterial()
            mhmat.populate_from_mhmat(found_material)
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

            from ....entities.objectproperties import GeneralObjectProperties
            GeneralObjectProperties.set_value("alternative_material", fragment, entity_reference=obj)

        self.report({'INFO'}, "Material was loaded: " + selected_material)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Library_Material_Operator)
