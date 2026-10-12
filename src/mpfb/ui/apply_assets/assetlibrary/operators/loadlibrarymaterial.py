"""Operator for loading an alternative material"""

import os
from bpy.props import StringProperty, BoolProperty
from .....services import LogService
from .....services import ObjectService
from .....services import MaterialService
from .....services import AssetService
from .....entities.clothes.mhclo import Mhclo
from .....entities.material.makeskinmaterial import MakeSkinMaterial
from .....entities.objectproperties import GeneralObjectProperties
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("assetlibrary.loadlibrarymaterial")

def _apply_mhmat(obj, mhmat_path):
    """Replace all materials on the object with the one defined by the given mhmat file."""

    if MaterialService.has_materials(obj):
        while len(obj.data.materials) > 0:
            obj.data.materials.pop(index=0)

    material = MaterialService.create_empty_material("makeskinmaterial", obj)

    mhmat = MakeSkinMaterial()
    mhmat.populate_from_mhmat(mhmat_path)
    mhmat.apply_node_tree(material)

    atype = str(ObjectService.get_object_type(obj)).lower().capitalize()
    colors = MaterialService.get_diffuse_colors()
    _LOG.dump("Colors, atype, exists", (colors, atype, atype in colors))
    color = (0.8, 0.8, 0.8, 1.0)

    if atype in colors:
        color = colors[atype]

    material.diffuse_color = color

def _find_default_material(obj, asset_subdir):
    """Find the material which the asset's mhclo file points at."""

    source = GeneralObjectProperties.get_value("asset_source", entity_reference=obj)
    if not source:
        _LOG.warn("Object does not have an asset source, so it has no default material", obj)
        return None

    mhclo_path = AssetService.find_asset_absolute_path(source, asset_subdir)
    _LOG.debug("Asset source, mhclo path", (source, mhclo_path))

    if not mhclo_path:
        return None

    mhclo = Mhclo()
    mhclo.load(mhclo_path, only_metadata=True)
    return mhclo.material

class MPFB_OT_Load_Library_Material_Operator(MpfbOperator):
    """Replace the current material with the selected alternative material"""
    bl_idname = "mpfb.load_library_material"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to material", default="")
    restore_default: BoolProperty(name="restore_default", description="Restore the material defined by the asset", default=False)

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):

        _LOG.debug("filepath", self.filepath)
        _LOG.debug("restore_default", self.restore_default)

        obj = context.active_object
        asset_subdir = str(ObjectService.get_object_type(obj)).lower()

        if self.restore_default:
            default_material = _find_default_material(obj, asset_subdir)
            if not default_material or not os.path.exists(str(default_material)):
                self.report({'ERROR'}, "Could not find the default material for this asset")
                return {'CANCELLED'}
            _apply_mhmat(obj, default_material)
            GeneralObjectProperties.set_value("alternative_material", "", entity_reference=obj)
            self.report({'INFO'}, "Default material was restored")
            return {'FINISHED'}

        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, "Could not find alternative material: " + str(self.filepath))
            return {'CANCELLED'}

        _apply_mhmat(obj, self.filepath)

        fragment = AssetService.path_to_fragment(self.filepath, asset_subdir=asset_subdir)
        _LOG.debug("Fragment", fragment)
        GeneralObjectProperties.set_value("alternative_material", fragment, entity_reference=obj)

        self.report({'INFO'}, "Material was loaded: " + os.path.basename(self.filepath))
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Material_Operator)
