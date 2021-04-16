"""Operator for creating a new human object."""

import bpy, os, gzip
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService
from mpfb import ClassManager
from mpfb.entities.socketobject import BASEMESH_EXTRA_GROUPS

_LOG = LogService.get_logger("newhuman.createhuman")

class MPFB_OT_CreateHumanOperator(bpy.types.Operator):
    """Create a new human"""
    bl_idname = "mpfb.create_human"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        from mpfb.ui.newhuman.newhumanpanel import NEW_HUMAN_PROPERTIES  # pylint: disable=C0415
        from mpfb.ui.newhuman import NewHumanObjectProperties  # pylint: disable=C0415

        exclude = []
        detailed_helpers = NEW_HUMAN_PROPERTIES.get_value("detailed_helpers", entity_reference=context.scene)
        extra_vertex_groups = NEW_HUMAN_PROPERTIES.get_value("extra_vertex_groups", entity_reference=context.scene)

        if not detailed_helpers:
            groups = ObjectService.get_base_mesh_vertex_group_definition()
            for group_name in groups.keys():
                if str(group_name).startswith("helper-") or str(group_name).startswith("joint-"):
                    exclude.append(str(group_name))

        if not extra_vertex_groups:
            # rather than extend in order to explicitly cast to str
            for group_name in BASEMESH_EXTRA_GROUPS.keys():
                exclude.append(str(group_name))
            exclude.extend(["Mid", "Right", "Left"])

        scale_factor = NEW_HUMAN_PROPERTIES.get_value("scale_factor", entity_reference=context.scene)
        scale = 0.1

        if scale_factor == "DECIMETER":
            scale = 1.0

        if scale_factor == "CENTIMETER":
            scale = 10.0

        basemesh = ObjectService.load_base_mesh(context=context, scale_factor=scale, load_vertex_groups=True, exclude_vertex_groups=exclude)
        _LOG.debug("Basemesh", basemesh)

        mask_helpers = NEW_HUMAN_PROPERTIES.get_value("mask_helpers", entity_reference=context.scene)

        if mask_helpers:
            modifier = basemesh.modifiers.new("Hide helpers", 'MASK')
            modifier.vertex_group = "body"
            modifier.show_in_editmode = True
            modifier.show_on_cage = True

        NewHumanObjectProperties.set_value("is_human_project", True, entity_reference=basemesh)

        add_phenotype = NEW_HUMAN_PROPERTIES.get_value("add_phenotype", entity_reference=context.scene)
        if add_phenotype:
            age = NEW_HUMAN_PROPERTIES.get_value("phenotype_age", entity_reference=context.scene)
            gender = NEW_HUMAN_PROPERTIES.get_value("phenotype_gender", entity_reference=context.scene)
            muscle = NEW_HUMAN_PROPERTIES.get_value("phenotype_muscle", entity_reference=context.scene)
            weight = NEW_HUMAN_PROPERTIES.get_value("phenotype_weight", entity_reference=context.scene)
            height = NEW_HUMAN_PROPERTIES.get_value("phenotype_height", entity_reference=context.scene)
            race = NEW_HUMAN_PROPERTIES.get_value("phenotype_race", entity_reference=context.scene)
            influence = NEW_HUMAN_PROPERTIES.get_value("phenotype_influence", entity_reference=context.scene)
            breast_firmness = NEW_HUMAN_PROPERTIES.get_value("phenotype_breastfirmness", entity_reference=context.scene)
            breast_size = NEW_HUMAN_PROPERTIES.get_value("phenotype_breastsize", entity_reference=context.scene)
            breast_influence = NEW_HUMAN_PROPERTIES.get_value("breast_influence", entity_reference=context.scene)
            add_breast = NEW_HUMAN_PROPERTIES.get_value("add_breast", entity_reference=context.scene)

            targets = LocationService.get_mpfb_data("targets")
            macrodetails = os.path.join(targets, "macrodetails")
            breast = os.path.join(targets, "breast")
            heightdir = os.path.join(macrodetails, "height")

            targets_to_load = []

            phenotype = os.path.join(macrodetails, "universal-" + gender + "-" + age + "-" + muscle + "-" + weight + ".target.gz")
            _LOG.debug("Selected universal phenotype", phenotype)
            targets_to_load.append([phenotype, influence])

            if race == "universal":
                races = ["african", "caucasian", "asian"]
                race_weight = 0.33
            else:
                races = [race]
                race_weight = 1.0

            for subrace in races:
                race_target = os.path.join(macrodetails, subrace + "-" + gender + "-" + age + ".target.gz")
                targets_to_load.append([race_target, race_weight])

            height_weight = influence
            if height == "average":
                height_weight = 0.0
                height = "maxheight"

            height_target = os.path.join(heightdir, gender + "-" + age + "-" + muscle + "-" + weight + "-" + height + ".target.gz")
            targets_to_load.append([height_target, height_weight])

            if add_breast:
                breast_target = os.path.join(breast, "female-" + age + "-" + muscle + "-" + weight + "-" + breast_size + "-" + breast_firmness + ".target.gz")
                targets_to_load.append([breast_target, breast_influence])

            _LOG.dump("Targets to load", targets_to_load)

            for target in targets_to_load:

                file_name = target[0]
                weight = target[1]
                name = os.path.basename(file_name).replace(".target.gz", "")

                _LOG.debug("File name", file_name)

                target_string = None
                if not os.path.exists(file_name):
                    raise IOError(file_name + " does not exist")
                target_string = None
                with gzip.open(file_name, "rb") as gzip_file:
                    raw_data = gzip_file.read()
                    target_string = raw_data.decode('utf-8')
                    if not target_string is None:
                        shape_key = TargetService.target_string_to_shape_key(target_string, name, basemesh)
                        shape_key.value = weight
                    else:
                        raise ValueError("Target string is None")

            self.report({'INFO'}, "Human created. You can adjust target weights amongst the new object's shape keys.")
        else:
            self.report({'INFO'}, "Human created.")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateHumanOperator)

