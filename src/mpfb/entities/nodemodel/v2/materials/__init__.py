from .abstractmaterialwrapper import AbstractMaterialWrapper

from .nodewrapperskin import NodeWrapperSkin

MATERIAL_WRAPPERS = dict()
MATERIAL_WRAPPERS["Skin"] = None

__all__ = [
    "AbstractMaterialWrapper",
    "MATERIAL_WRAPPERS",
    "NodeWrapperSkin"
    ]
