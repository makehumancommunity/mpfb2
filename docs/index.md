# Docs

These are some basic technical docs intended for developers. For more elaborate and user friendly documentation, see
the [docs hierarchy](https://static.makehumancommunity.org/mpfb/docs.html) on the website.

## Code structure

- [Code Structure Guide](code-structure.md) — how the codebase is organized, for new developers

## File formats

These are format descriptions for various files used by MPFB.

### MakeHuman file formats

These describe the formats of files used by both MakeHuman and MPFB:

- [MHM](fileformats/mhm.md)
- [MHCLO](fileformats/mhclo.md)
- [MHMAT](fileformats/mhmat.md)
- [Target](fileformats/target.md)

### MPFB JSON file formats

These describe JSON formats used internally by MPFB and for user presets:

- [Rig definition](fileformats/rig.md) — bone hierarchy and position strategies
- [Vertex weights](fileformats/weights.md) — bone-to-vertex weight assignments
- [Pose](fileformats/pose.md) — static bone rotations (system and user poses)
- [Node tree / shader](fileformats/node_tree.md) — Blender shader node network definitions
- [Material settings](fileformats/material_settings.md) — enhanced skin and eye parameter presets
- [Target metadata](fileformats/target_metadata.md) — target categories and macro morph definitions
- [Mesh metadata](fileformats/mesh_metadata.md) — vertex groups, mesh config, UV layers
- [Human preset](fileformats/human_preset.md) — complete character definition
- [Miscellaneous presets](fileformats/misc_presets.md) — importer presets, makeup, ink layers

## Services

API documentation for the service layer in `src/mpfb/services/`.

### Foundational

- [LogService](services/logservice.md) — logging and profiling infrastructure
- [LocationService](services/locationservice.md) — file system path resolution

### Configuration utilities

- [ConfigurationSet](services/configurationset.md) — abstract base for configuration management
- [BlenderConfigSet](services/blenderconfigset.md) — Blender entity property management (ie storing configuration on an object)
- [SceneConfigSet](services/sceneconfigset.md) — scene-level property configuration (ie storing configuration in the scene)
- [DynamicConfigSet](services/dynamicconfigset.md) — object configuration with dynamic properties
- [JsonCall](services/jsoncall.md) — JSON-serializable function call model. This is only used in communication with a running MakeHuman instance.

### Standalone services

- [SystemService](services/systemservice.md) — platform detection and system utilities
- [ObjectService](services/objectservice.md) — Blender object creation and management
- [ModifierService](services/modifierservice.md) — Blender modifier operations
- [NodeService](services/nodeservice.md) — shader node tree and node manipulation
- [NodeTreeService](services/nodetreeservice.md) — node tree interface socket utilities
- [MeshService](services/meshservice.md) — mesh, vertex group, and spatial operations
- [SocketService](services/socketservice.md) — MakeHuman socket server communication
- [UiService](services/uiservice.md) — UI state and preset list management

### Higher-level services

- [AssetService](services/assetservice.md) — asset discovery, caching, and pack management
- [MaterialService](services/materialservice.md) — material creation and management
- [TargetService](services/targetservice.md) — shape key and morph target management
- [RigService](services/rigservice.md) — armature, bone, weight, and pose operations
- [AnimationService](services/animationservice.md) — BVH import and keyframe manipulation

### Aggregator services

- [ClothesService](services/clothesservice.md) — clothes fitting, rigging, and MHCLO management
- [HumanService](services/humanservice.md) — high-level character creation and serialization
- [HairEditorService](services/haireditorservice.md) — hair and fur asset management
