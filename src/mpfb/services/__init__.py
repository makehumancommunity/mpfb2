"""Package with all services."""

# Order matters, since the services rely on each other.
# Everything depends on LogService, which has no dependencies.
from .logservice import LogService

_LOG = LogService.get_logger("services.init")
_LOG.trace("initializing services module")

# LocationService only depends on LogService.
from .locationservice import LocationService

# Utility classes
from .jsoncall import JsonCall
from .configurationset import ConfigurationSet
from .blenderconfigset import BlenderConfigSet
from .sceneconfigset import SceneConfigSet

# Mostly standalone services
from .modifierservice import ModifierService
from .nodeservice import NodeService
from .nodetreeservice import NodeTreeService
from .objectservice import ObjectService
from .socketservice import SocketService
from .systemservice import SystemService
from .uiservice import UiService

# Services only depending on the standalone services
from .assetservice import AssetService, ASSET_LIBRARY_SECTIONS
from .materialservice import MaterialService
from .meshservice import MeshService

# Next layer of aggregation
from .targetservice import TargetService
from .rigservice import RigService
from .animationservice import AnimationService

# Depend on everything services
from .clothesservice import ClothesService
from .humanservice import HumanService

__all__ = [
    "LogService",
    "LocationService",
    "JsonCall",
    "ConfigurationSet",
    "BlenderConfigSet",
    "SceneConfigSet",
    "ModifierService",
    "NodeService",
    "NodeTreeService",
    "ObjectService",
    "SocketService",
    "SystemService",
    "UiService",
    "AssetService",
    "MaterialService",
    "MeshService",
    "TargetService",
    "RigService",
    "AnimationService",
    "ClothesService",
    "HumanService",
    "ASSET_LIBRARY_SECTIONS"
    ]
