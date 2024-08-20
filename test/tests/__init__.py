import importlib, sys


def dynamic_import(absolute_package_str, key):
    for amod in sys.modules:
        if amod.endswith(absolute_package_str):
            mpfb_mod = importlib.import_module(amod)

            if not hasattr(mpfb_mod, key):
                raise AttributeError(f"Module {amod} does not have attribute {key}")

            return getattr(mpfb_mod, key)


MPFB_CONTEXTUAL_INFORMATION = dynamic_import("mpfb", "MPFB_CONTEXTUAL_INFORMATION")

AnimationService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["AnimationService"]
AssetService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["AssetService"]
ClothesService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["ClothesService"]
HumanService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["HumanService"]
LocationService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["LocationService"]
LogService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["LogService"]
MaterialService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["MaterialService"]
MeshService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["MeshService"]
ModifierService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["ModifierService"]
NodeService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["NodeService"]
NodeTreeService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["NodeTreeService"]
ObjectService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["ObjectService"]
RigService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["RigService"]
SocketService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["SocketService"]
SystemService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["SystemService"]
TargetService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["TargetService"]
UiService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["UiService"]

