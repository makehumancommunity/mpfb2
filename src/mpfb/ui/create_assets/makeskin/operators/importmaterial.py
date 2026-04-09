"""Operator for importing MHMAT material."""

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from .....entities.material.makeskinmaterial import MakeSkinMaterial
from .....services import LogService
from .....services import MaterialService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("makeskin.importmaterial")

@pollstrategy(PollStrategy.ANY_MAKEHUMAN_OBJECT_ACTIVE)
class MPFB_OT_ImportMaterialOperator(MpfbOperator, ImportHelper):
    """Import MHMAT"""
    bl_idname = "mpfb.import_makeskin_material"
    bl_label = "Import material"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.mhmat', options={'HIDDEN'})

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        from ...makeskin.makeskinpanel import MAKESKIN_PROPERTIES  # pylint: disable=C0415
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=MAKESKIN_PROPERTIES)

        if MaterialService.has_materials(ctx.active_object):
            if not ctx.overwrite:
                self.report({'ERROR'}, "A material for this object already exists, change 'replace' option in common settings to overwrite material")
                return {'FINISHED'}
            else:
                while len(ctx.active_object.data.materials) > 0:
                    ctx.active_object.data.materials.pop(index=0)

        material = MaterialService.create_empty_material("makeskinmaterial", ctx.active_object)

        mhmat = MakeSkinMaterial()
        mhmat.populate_from_mhmat(self.filepath)
        mhmat.apply_node_tree(material)

        self.report({'INFO'}, "Material imported")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ImportMaterialOperator)
