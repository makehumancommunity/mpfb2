"""Shared type aliases for the MPFB services and entities layers.

This module exists so that type shapes which cross more than one module are declared once
rather than redefined per module. It deliberately imports nothing from MPFB, so that
importing it can never disturb the deferred-import rule in ``__init__.py`` or introduce a
cycle between services. It is annotation support only and must not gain runtime logic.
"""

from collections.abc import Callable
from typing import Any

PropertyDefinition = dict[str, Any]
"""The dict shape describing a single blender property in a ConfigurationSet.

Recognized keys are ``name`` (the short, unprefixed name), ``type`` (one of ``boolean``,
``string``, ``path``, ``dir_path``, ``int``, ``float``, ``vector_location``, ``color`` or
``enum``), ``description`` and ``default``, plus the optional ``label``, ``subtype``,
``aliases``, ``min``, ``max`` and ``items``. ``BlenderConfigSet`` adds ``full_name``, the
prefixed name the property is actually registered under, to its own copy of the dict.

This is an alias rather than a ``TypedDict`` on purpose: these dicts are read straight from
JSON, copied with ``dict()``, and then extended in place with ``full_name``, none of which a
``TypedDict`` models well.
"""

PropertyAccessorFactory = Callable[[Any, str], Any]
"""A factory which builds a blender property get/set callback for a single property.

It is called with the ConfigurationSet the property belongs to and the short name of that
property, and returns the callback to hand to ``bpy.props`` as ``get=`` or ``set=``. The
configuration set is typed as ``Any`` rather than ``ConfigurationSet`` so that this module
stays free of MPFB imports; the returned callback is typed as ``Any`` because its own
signature depends on the property type it is being built for.
"""

BoneInfo = dict[str, Any]
"""Everything a rig definition records about a single bone.

The stable keys are ``parent`` (a bone name or the empty string), ``head`` and ``tail`` (each a
nested dict, see ``entities.rig.BoneEndInfo``), ``use_connect``, ``use_local_location``,
``use_inherit_rotation``, ``inherit_scale``, ``collections`` (a sorted list of bone collection
names) and ``roll``. ``bendy_bone``, ``rotation_mode``, ``constraints``, ``roll_strategy``,
``roll_reference_z`` and ``rigify`` are present only when they carry something. Version 100
definitions instead carried ``layers``, a 32 element bool list, which ``Rig._upgrade_definition()``
rewrites into ``collections``.

An alias rather than a ``TypedDict`` because the dict is built up across four passes --
``add_data_bone_info()``, ``add_edit_bone_info()``, ``add_pose_bone_info()`` and the strategy
matching -- so no single point in the code sees the complete shape, and because ``cleanup_float_values()``
reads and rewrites several entries through computed keys."""

RigDefinition = dict[str, BoneInfo]
"""The ``bones`` section of a rig file: bone name to its ``BoneInfo``."""

RigHeader = dict[str, Any]
"""The top level of a rig file.

``version`` holds the format version as an int and ``bones`` holds the ``RigDefinition``; both are
always present. ``is_subrig`` is a bool, ``scale_factor`` a float, ``collections`` a list of bone
collection names, ``extra_bones`` a list of bone names and ``rigify_ui`` a ``RigifyUi``. An alias
rather than a ``TypedDict`` because a version 100 file has only the two mandatory keys, so every
other entry is read with ``get()`` and may be absent."""

RigifyUi = dict[str, Any]
"""The rigify colour and bone collection settings carried in a rig file's ``rigify_ui`` entry.

``rigify_colors_lock`` is a bool, ``selection_colors`` a dict with ``select`` and ``active``,
``colors`` a list of ``{name, normal}`` dicts, and ``collections`` a dict keyed by bone collection
name holding ``is_visible``, ``ui_row``, ``ui_title``, ``sel_set`` and ``color_set_id``. A version
100 file instead carries ``layers`` and ``rigify_layers``, which
``RigifyHelpers.upgrade_rigify_ui_layers()`` replaces with ``collections``. An alias and not a
``TypedDict`` precisely because of that rewrite: the same dict holds the old keys on the way in and
the new ones on the way out."""

RigifyBoneInfo = dict[str, Any]
"""The ``rigify`` entry of a ``BoneInfo``.

``rigify_type`` holds the name of a rigify rig class and ``rigify_parameters`` a dict of that
class's parameters. Both are optional, and an empty dict is the normal state for a bone rigify does
not drive. The parameter values are whatever the rigify add-on registered, so they are read and
written as ``Any``."""

RigHelperSettings = dict[str, Any]
"""The settings dict the rig helper classes under ``entities.rigging.righelpers`` are constructed with.

It is a ``SceneConfigSet.as_dict()`` result, so the keys are the short names of the helper
properties -- ``arm_helpers_type``, ``leg_helpers_type``, ``finger_helpers_type``,
``eye_parenting_strategy``, ``hide_fk`` and the rest -- and the values arrive as ``Any``. An alias
rather than a ``TypedDict`` both for that reason and because the helpers test for membership before
reading, since a caller may hand over a dict built for one limb only."""

RigifySettings = dict[str, Any]
"""The settings dict ``RigifyHelpers`` is constructed with.

A separate name from ``RigHelperSettings`` because it is a different property set -- ``name``,
``produce`` and ``meta_rig_action`` -- even though the two definitions coincide. Same reasoning for
the alias: the values come from ``SceneConfigSet.as_dict()`` as ``Any`` and are read with
``in``/``get()``."""

BoneOrientation = dict[str, Any]
"""The recorded position of one bone, as ``RigService.get_bone_orientation_info_as_dict()`` writes it.

``head``, ``tail`` and ``matrix`` are ``mathutils`` copies and are present for both pose and edit
bones. An edit bone entry additionally carries ``roll`` and ``length`` as floats and ``parent`` as a
bone name or the empty string. An alias and not a ``TypedDict`` because the two variants share one
dict type and the pose variant has only three of the six keys."""

BoneOrientationInfo = dict[str, dict[str, BoneOrientation]]
"""A snapshot of the positions of every bone in an armature.

Two keys, ``pose_bones`` and ``edit_bones``, each mapping a bone name to its ``BoneOrientation``.
The rig helpers take this snapshot before entering edit mode, because the values they need are
readable in one mode and the bones they create in the other."""

HumanInfo = dict[str, Any]
"""The character definition dictionary: MPFB's own save format for a human.

It is what ``HumanService`` writes as ``human.<name>.json``, what it reads back, and what an MHM
file is parsed into. ``phenotype`` holds a ``MacroInfo`` and ``targets`` a list of
``TargetStackEntry``. ``rig``, ``eyes``, ``eyebrows``, ``eyelashes``, ``tongue``, ``teeth``,
``hair``, ``proxy``, ``skin_mhmat``, ``skin_material_type`` and ``eyes_material_type`` hold strings,
``clothes``, ``makeup`` and ``expressions`` lists, and ``skin_material_settings``,
``eyes_material_settings``, ``alternative_materials`` and ``color_adjustments`` nested dicts. ``name``
and ``material_instances`` are added by the loading path rather than stored in the file.

An alias rather than a ``TypedDict`` for three reasons: a preset written by an older MPFB carries only
a subset of the keys, so almost every read goes through ``in`` or ``get()``; the values arrive from
``json.load()`` as ``Any``; and the deserialization path writes ``material_instances`` and ``name``
into the same dict it was handed, so no single point in the code sees one fixed shape."""

DeserializationSettings = dict[str, Any]
"""The settings dict which controls how a ``HumanInfo`` is turned back into a character.

``HumanService.get_default_deserialization_settings()`` builds one with ``mask_helpers``,
``detailed_helpers``, ``extra_vertex_groups``, ``feet_on_ground``, ``load_clothes``, ``scale``,
``subdiv_levels``, ``override_skin_model``, ``override_rig`` and ``material_instances``. The MHM path
additionally requires ``clothes_deep_search`` and ``bodypart_deep_search``, which the defaults do not
contain, and ``override_clothes_model`` and ``override_eyes_model`` are read with ``in`` when present.

An alias rather than a ``TypedDict`` precisely because of that split: the mandatory key set differs
between the three entry points, and the UI layer builds the dict by copying the defaults and then
overwriting entries from a ``SceneConfigSet``, whose values arrive as ``Any``."""

SocketMeshInfo = dict[str, Any]
"""The description of one mesh which MakeHuman's socket server sends ahead of its geometry.

Two calls produce one: ``SocketService.get_body_mesh_info()`` for the base mesh, and each entry of
the list ``SocketService.get_proxies_info()`` returns for a proxy (clothes, eyes, a body proxy and so
on). The two do not carry the same keys, which is why this is one shape rather than two. Both carry
``name`` and the ``verticesShape``, ``verticesTypeCode``, ``facesShape``, ``facesTypeCode``,
``textureCoordsShape``, ``textureCoordsTypeCode``, ``faceUVMappingsShape`` and
``faceUVMappingsTypeCode`` entries which ``SocketMeshObject.convert_to_shaped_numpy_array()`` reads in
order to reshape the matching binary call's payload. The base mesh additionally carries ``filename``,
``faceGroups`` and ``faceMask``; a proxy carries ``type`` and ``uuid``, and reports its sizes as
``numVertices``, ``numFaces``, ``numTextureCoords`` and ``numFaceUVMappings`` instead of the four
``*Shape`` entries, which ``SocketProxyObject`` fills in from them.

An alias rather than a ``TypedDict`` for that reason: no single shape describes both producers, the
values arrive from ``json.loads()`` as ``Any``, and ``SocketProxyObject.__init__()`` extends the dict
it was handed with the four missing ``*Shape`` entries."""

SocketWeightInfo = dict[str, Any]
"""The vertex weight index which MakeHuman's socket server sends ahead of the weights themselves.

``SocketService.get_body_weight_info()`` and ``SocketService.get_proxy_weight_info()`` both return
one. The single key read in MPFB is ``weights``, a list with one entry per weighted bone, each
carrying ``bone`` (the bone name) and ``numVertices`` (how many of the following vertex indices and
weight values belong to it). ``SocketMeshObject.arrange_weights()`` walks that list in order to slice
the two parallel binary payloads into per bone arrays, so the order of the list is significant."""

SocketSkeletonInfo = dict[str, Any]
"""The skeleton which MakeHuman's socket server describes for the currently loaded character.

``SocketService.get_skeleton()`` returns one. The keys read in MPFB are ``name``, which is the string
``"none"`` when the character has no skeleton, and ``bones``, a list of root bones each of which
nests its own ``children``. ``RigService.create_rig_from_skeleton_info()`` consumes the latter.

This is not the same shape as ``RigDefinition``, which is MPFB's own rig file format: a
``SocketSkeletonInfo`` nests its bones as a tree and arrives over the socket, where a
``RigDefinition`` is flat, is keyed by bone name and is read from a file."""

NodeInfo = dict[str, Any]
"""The version 1 description of a single shader node, as ``NodeService.get_node_info()`` writes it.

``type`` holds the node's class name, ``name`` and ``label`` its own, ``location`` a two element
list of floats and ``create`` a bool which is always ``True`` on the way out. ``values`` maps the
name of each float, float-factor or colour input socket to its default value, which is a float for
the first two and a four element list for a colour. The remaining keys are per node type:
``filename`` and ``colorspace`` for an image texture, ``operation`` and ``use_clamp`` for a maths
node, ``operation`` alone for a vector maths node, and ``value`` for a value node.
``get_node_tree_as_dict()`` additionally writes ``group_name`` for a group node, and
``apply_node_tree_from_dict()`` reads a ``stops`` list for a colour ramp which nothing in MPFB
writes.

This is the shape the node tree templates under ``data/node_trees`` are written in, so it is also
what a hand edited template has to produce. It is read by ``MaterialService`` and by the two
material entities as well as by ``NodeService`` itself, which is why it lives here.

An alias rather than a ``TypedDict`` because the per node type keys make the shape depend on the
value of ``type``, because the templates arrive through ``json.load()`` as ``Any``, and because
``create`` is read with ``in`` -- a template entry which omits it is treated as present and true."""

NodeTreeDict = dict[str, Any]
"""A whole shader node tree as a dict: its nodes, its links and the groups they refer to.

``nodes`` maps a node name to its ``NodeInfo`` and ``links`` is a list of the dicts
``NodeService.get_link_info()`` produces. ``groups``, which only the outermost level carries, maps
a group name to a nested ``NodeTreeDict`` which additionally carries that group's own ``inputs``
and ``outputs`` interface declarations, and which ``_ensure_group_interfaces_exist()`` extends in
place with ``pre_existing``.

``NodeService.get_node_tree_as_dict()`` produces one and ``apply_node_tree_from_dict()`` consumes
one, but the common case is neither: the dict is read from a template under ``data/node_trees`` by
the material entities and by ``HumanService``, which is why it lives here rather than in the
service.

An alias rather than a ``TypedDict`` because ``groups`` is present at one recursion level and not
at the others, because the group entries hold two key sets at once -- a nested tree plus the
interface declarations -- and because every value arrives from ``json.load()`` as ``Any``."""

SocketValues = dict[str, Any]
"""Input socket name to default value, for the sockets whose value MPFB reads and writes.

``NodeService.get_socket_default_values()`` produces one and ``set_socket_default_values()``
consumes one, and both restrict themselves to ``NodeSocketColor``, ``NodeSocketFloatFactor`` and
``NodeSocketFloat`` sockets. So a value is either a float or, for a colour, a four element list.
It crosses the layer boundary in both directions: ``HumanService`` stores one per node group as a
character's material settings, and ``MakeSkinMaterial`` reads one to recover MHMAT values from a
node tree.

``Any`` rather than ``float | list[float]`` as the value type because the dicts are also written
to and read back from JSON, where the colour arrives as a plain list and is handed straight to a
socket. ``MaterialService.ColorAdjustment`` is the same shape under a name which says what one
particular such dict is for."""
