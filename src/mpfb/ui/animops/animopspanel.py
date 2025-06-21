import os, bpy
from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import ObjectService
from ...services import SceneConfigSet
from ...services import UiService
from ...services import MaterialService
from ...services import RigService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("animops.animopspanel")

_LOC = os.path.dirname(__file__)
ANIMOPS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
ANIMOPS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(ANIMOPS_PROPERTIES_DIR, prefix="ANIO_")

class MPFB_PT_AnimopsPanel(Abstract_Panel):
    bl_label = "Animation"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def _map_mixamo(self, scene, layout):
        box = self.create_box(layout, "Map mixamo")
        armatures = ObjectService.get_selected_armature_objects()
        if len(armatures) != 2:
            box.label(text="Select two mixamo armatures")
            return
        if RigService.identify_rig(armatures[0]) != "mixamo" or RigService.identify_rig(armatures[1]) != "mixamo":
            box.label(text="Only mixamo armatures supported")
            return
        src = None
        dst = None
        bm1 = ObjectService.find_object_of_type_amongst_nearest_relatives(armatures[0], "Basemesh")
        bm2 = ObjectService.find_object_of_type_amongst_nearest_relatives(armatures[1], "Basemesh")
        if bm1 and not bm2:
            src = armatures[1]
            dst = armatures[0]
        if bm2 and not bm1:
            src = armatures[0]
            dst = armatures[1]
        if not src:
            src = bpy.context.object
            if src == armatures[0]:
                dst = armatures[1]
            else:
                dst = armatures[0]
        box.label(text="Source: %s" % src.name)
        box.label(text="Dest: %s" % dst.name)
        box.operator("mpfb.map_mixamo")

    def _create_mixamo(self, scene, layout):
        box = self.create_box(layout, "Reduced doll")
        ANIMOPS_PROPERTIES.draw_properties(scene, box, ["call_fbx"])
        box.operator("mpfb.reduced_doll")

    def _make_cyclic(self, scene, layout):
        box = self.create_box(layout, "Make cyclic")
        ANIMOPS_PROPERTIES.draw_properties(scene, box, ["shiftroot"])
        shiftroot = ANIMOPS_PROPERTIES.get_value("shiftroot", entity_reference=scene)
        if shiftroot:
            ANIMOPS_PROPERTIES.draw_properties(scene, box, ["rootbone"])
        box.operator("mpfb.make_cyclic")

    def _repeat_anim(self, scene, layout):
        box = self.create_box(layout, "Repeat animation")
        ANIMOPS_PROPERTIES.draw_properties(scene, box, ["iterations", "offset", "skipfirst", "shiftroot"])
        shiftroot = ANIMOPS_PROPERTIES.get_value("shiftroot", entity_reference=scene)
        if shiftroot:
            ANIMOPS_PROPERTIES.draw_properties(scene, box, ["firstframe", "rootbone"])
        box.operator("mpfb.repeat_animation")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        _LOG.debug("Object", context.object)
        if context.object is None:
            return

        self._create_mixamo(scene, layout)

        _LOG.debug("Type", context.object.type)
        if context.object.type != "ARMATURE":
            return

        self._map_mixamo(scene, layout)
        self._make_cyclic(scene, layout)
        self._repeat_anim(scene, layout)

ClassManager.add_class(MPFB_PT_AnimopsPanel)
