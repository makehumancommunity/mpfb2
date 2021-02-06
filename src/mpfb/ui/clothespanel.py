#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb import CLASSMANAGER
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
import bpy

_LOG = LogService.get_logger("ui.clothespanel")

class MPFB_PT_Clothes_Panel(bpy.types.Panel):
    bl_label = "Clothes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("CLOTHESCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene

CLASSMANAGER.add_class(MPFB_PT_Clothes_Panel)
