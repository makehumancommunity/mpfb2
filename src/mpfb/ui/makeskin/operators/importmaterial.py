#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb.services.uiservice import UiService
from mpfb import ClassManager
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.entities.material.enhancedskinmaterial import EnhancedSkinMaterial
import bpy, os, json
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

_LOG = LogService.get_logger("makeskin.importmaterial")

class MPFB_OT_ImportMaterialOperator(bpy.types.Operator, ImportHelper):
    """Import MHMAT"""
    bl_idname = "mpfb.import_makeskin_material"
    bl_label = "Import material"
    bl_options = {'REGISTER','UNDO'}

    filter_glob: StringProperty(default='*.mhmat', options={'HIDDEN'})

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            return True
        return False

    def execute(self, context):
        obj = context.active_object
        scn = context.scene

#===============================================================================
#         if hasMaterial(obj):
#             if not scn.MhMsOverwrite:
#                 self.report({'ERROR'}, "A material for this object already exists, change 'replace' option in common settings to overwrite material")
#                 return {'FINISHED'}
#             else:
#                 while len(obj.data.materials) > 0:
#                     obj.data.materials.pop(index=0)
#
#         mhmat = MHMat(fileName=self.filepath)
#         mhmat.assignAsNodesMaterialForObj(scn, obj, True)
#
#         ##- Load Blend -##
#         path = mhmat.settings["blendMaterial"]
#         if path:
#             blendMatLoad(path)
#
#         self.report({'INFO'}, "Material imported")
#===============================================================================
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ImportMaterialOperator)
