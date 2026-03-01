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

### High level services

These are the top level services which abstract the functionality in MPFB. This is where you should start looking if
you want to do something.

- [HumanService](services/humanservice.md) — high-level character creation and serialization. This is the central service of MPFB.
- [AssetService](services/assetservice.md) — asset discovery, caching, and pack management
- [MaterialService](services/materialservice.md) — material creation and management
- [TargetService](services/targetservice.md) — shape key and morph target management
- [RigService](services/rigservice.md) — armature, bone, weight, and pose operations
- [ClothesService](services/clothesservice.md) — clothes fitting, rigging, and MHCLO management

### System, infrastructure and configuration

These are services which are used throughout most of the code:

- [LogService](services/logservice.md) — logging and profiling infrastructure
- [LocationService](services/locationservice.md) — file system path resolution
- [SystemService](services/systemservice.md) — platform detection and system utilities

These are configuration-related helper classes:

- [ConfigurationSet](services/configurationset.md) — abstract base for configuration management
- [BlenderConfigSet](services/blenderconfigset.md) — Blender entity property management (ie storing configuration on an object)
- [SceneConfigSet](services/sceneconfigset.md) — scene-level property configuration (ie storing configuration in the scene)
- [DynamicConfigSet](services/dynamicconfigset.md) — object configuration with dynamic properties

### Utility services

These are helper services:

- [ObjectService](services/objectservice.md) — Blender object creation and management
- [ModifierService](services/modifierservice.md) — Blender modifier operations
- [NodeService](services/nodeservice.md) — shader node tree and node manipulation
- [NodeTreeService](services/nodetreeservice.md) — node tree interface socket utilities
- [MeshService](services/meshservice.md) — mesh, vertex group, and spatial operations
- [UiService](services/uiservice.md) — UI state and preset list management

### Services for specific or experimental functionality

These services are either abstractions for a specific feature, or experimental. Unless you work with these specific
topics, it is unlikely you will need them elsewhere in the code.

- [AnimationService](services/animationservice.md) — BVH import and keyframe manipulation. Mostly experimental.
- [ExportService](services/exportservice.md) — character copy creation, shape key interpolation, and modifier baking for export to external applications
- [HairEditorService](services/haireditorservice.md) — Hair and fur asset management. Experimental and only useful for the hair editor.

### Communication with MakeHuman

These are services and classes which are only relevant when interacting with a running MakeHuman instance.

- [SocketService](services/socketservice.md) — MakeHuman socket server communication
- [JsonCall](services/jsoncall.md) — JSON-serializable function call model. 

## Entities

Entity classes are in `src/mpfb/entities/`. Entities are data-oriented classes that encapsulate state and domain logic, in contrast to the stateless singleton services.
In many cases, an entity class is a wrapper for a file format (see above).

### Data structures and utilities

- [MeshCrossRef](entities/meshcrossref.md) — multi-table mesh cross-reference for efficient spatial and topological queries
- [PrimitiveProfiler](entities/primitiveprofiler.md) — lightweight named timing profiler for development use

### Object property sets

- [Object properties](entities/objectproperties.md) — `GeneralObjectProperties`, `HumanObjectProperties`, and `SkeletonObjectProperties`: module-level `BlenderConfigSet` singletons that attach namespaced custom properties to Blender objects

### Clothes entities

- [Mhclo](entities/clothes/mhclo.md) — parser and serializer for MHCLO clothing files
- [VertexMatch](entities/clothes/vertexmatch.md) — automatic clothes-to-basemesh vertex mapping with 4-strategy fallback

### Material entities

- [MHMAT key system](entities/material/mhmat_keys.md) — type hierarchy and key catalog for MHMAT parsing (`mhmatkeytypes.py`, `mhmatkeys.py`)
- [MhMaterial](entities/material/mhmaterial.md) — parser and serializer for MHMAT material files
- [MakeSkinMaterial](entities/material/makeskinmaterial.md) — bridges MHMAT format with Blender node-based materials (MakeSkin workflow)
- [EnhancedSkinMaterial](entities/material/enhancedskinmaterial.md) — advanced skin shader with PBR and subsurface scattering support

### Rig entity

- [Rig](entities/rig.md) — armature serialisation/deserialisation and JSON Blender round-trip, with positioning-strategy system

### Rigging helpers

Yes it looks odd that each helper is a one-to-one class hierarchy. "Default" here is the "default" rig. The plan was originally
to support other rigs too.

- [AbstractRigHelper](entities/rigging/righelpers.md) — base class providing Blender mode-switching utilities
- [ArmHelpers / DefaultArmHelpers](entities/rigging/armhelpers.md) — IK helper bones and constraints for arms
- [LegHelpers / DefaultLegHelpers](entities/rigging/leghelpers.md) — IK helper bones and constraints for legs
- [EyeHelpers / DefaultEyeHelpers](entities/rigging/eyehelpers.md) — eye-tracking IK bones and constraints
- [FingerHelpers / DefaultFingerHelpers](entities/rigging/fingerhelpers.md) — grip and IK helpers for fingers
- [RigifyHelpers / GameEngineRigifyHelpers](entities/rigging/rigifyhelpers.md) — Rigify metarig conversion

