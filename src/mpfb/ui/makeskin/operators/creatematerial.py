#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.socketservice import SocketService
from mpfb.services.objectservice import ObjectService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb.services.uiservice import UiService
from mpfb.ui.importer.importerpanel import IMPORTER_PROPERTIES
from mpfb.ui.importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from mpfb import ClassManager
from mpfb.entities.socketobject.socketbodyobject import SocketBodyObject
from mpfb.entities.socketobject.socketproxyobject import SocketProxyObject
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.entities.material.enhancedskinmaterial import EnhancedSkinMaterial
import bpy, os, json

_LOG = LogService.get_logger("makeskin.creatematerial")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_CreateMaterialOperator(bpy.types.Operator):
    """Create template material"""
    bl_idname = "mpfb.create_makeskin_material"
    bl_label = "Create material"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            return context.active_object.type == "MESH"
        return False

    def execute(self, context):

        object = context.active_object
        scene = context.scene

        from mpfb.ui.makeskin.makeskinpanel import MAKESKIN_PROPERTIES
        from mpfb.ui.makeskin import MakeSkinObjectProperties

        overwrite = MAKESKIN_PROPERTIES.get_value("overwrite", entity_reference=scene)

        if not overwrite and MaterialService.has_materials(object):
            self.report({'ERROR'}, "Object already has a material")
            return {'FINISHED'}

        if overwrite and MaterialService.has_materials(object):
            MaterialService.delete_all_materials(object)

        name = MakeSkinObjectProperties.get_value("name", entity_reference=object)
        if not name:
            name = "MakeSkinMaterial"

        MakeSkinMaterial.create_makeskin_template_material(object, scene, name)

        self.report({'INFO'}, "Material was created")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateMaterialOperator)
