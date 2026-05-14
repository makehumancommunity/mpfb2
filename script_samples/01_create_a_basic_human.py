# ------------------------------------------------------------------------------------------
# This quirk needs to be copy/pasted into every script. Blender extensions end up
# on unknown places in the module hierarchy, so at write time you don't know the
# absolute package name. Thus we iterate over all modules known by sys to find 
# a package and a the key of a declared symbol
# 
import importlib, sys
def dynamic_import(absolute_package_str, key):
    """Quirk to get around blender's extension format's requirement that all imports must be relative"""
    for amod in sys.modules:
        if amod.endswith(absolute_package_str):
            mpfb_mod = importlib.import_module(amod)
            if not hasattr(mpfb_mod, key):
                raise AttributeError(f"Module {amod} does not have attribute {key}")
            return getattr(mpfb_mod, key)
    raise ValueError(f"No module found with name ending in {absolute_package_str}")
#
# ------------------------------------------------------------------------------------------

# Equivalent of imports
HumanService = dynamic_import("mpfb.services.humanservice", "HumanService")
TargetService = dynamic_import("mpfb.services.targetservice", "TargetService")
HumanObjectProperties = dynamic_import("mpfb.entities.objectproperties", "HumanObjectProperties")

# Simplest possible case
neutral_human = HumanService.create_human()
neutral_human.location = (-1, 0, 0)

# caucasian woman 
caucasian_woman = HumanService.create_human()
caucasian_woman.location = (1, 0, 0)

HumanObjectProperties.set_value("african", 0.0, entity_reference=caucasian_woman)
HumanObjectProperties.set_value("asian", 0.0, entity_reference=caucasian_woman)
HumanObjectProperties.set_value("caucasian", 0.0, entity_reference=caucasian_woman)
HumanObjectProperties.set_value("gender", 1.0, entity_reference=caucasian_woman)

TargetService.reapply_macro_details(caucasian_woman)
