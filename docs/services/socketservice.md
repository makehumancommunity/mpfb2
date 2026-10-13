# SocketService

## Overview

SocketService is one of the more ancient of the services, tracing its roots back to when the main purpose of MPFB was to interact with 
a running MakeHuman instance. It has little use beyond that purpose.

SocketService handles asynchronous communication with a separate MakeHuman socket server. It manages JSON and binary remote calls for retrieving mesh data, material information, skeleton data, and proxy asset information from a running MakeHuman instance.

Unlike most MPFB services which are static classes, SocketService is instantiated as a module-level singleton. This is because it maintains connection state (host, port) and a result cache across multiple calls.

The service uses Python's `asyncio` library for non-blocking network I/O. It supports two types of remote calls: **JSON calls** for structured data (mesh metadata, material info, skeleton definitions) and **binary calls** for large numeric data (vertex positions, face indices, weights). Binary transfers are significantly more efficient for bulk geometry data.

The socket protocol is defined by MakeHuman's socket server API. Each call sends a function name and optional parameters as JSON, and receives either a JSON response or raw binary data depending on the function. See [JsonCall](jsoncall.md) for details on the call format.

SocketService caches results for certain calls (like directory paths) to avoid repeated network round-trips for static information.

**Every JSON call can return `None`.** A `JsonCall` is constructed with no data, and the reply parser only assigns one when the reply carried a non-empty `data` entry. MakeHuman answers a call it cannot serve by filling in the reply's `error` field and leaving `data` empty, and SocketService never inspects `error`, so a failed call and a successful call which carried nothing are indistinguishable: both arrive as `None`. Callers are expected to check, and the socket object entities under `src/mpfb/entities/socketobject` currently do not — see [SocketObject](../entities/socketobject.md).

The binary calls are **not** nullable. The binary path assigns a `bytearray` unconditionally, even when what the server sent was a JSON error message rather than geometry, so a failed binary call surfaces as a short or unparseable buffer rather than as `None`.

## Source

`src/mpfb/services/socketservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.socketservice")` |
| `JsonCall` | JSON-serializable function call model |
| `mpfb.types` | `SocketMeshInfo`, `SocketWeightInfo` and `SocketSkeletonInfo`, the shared aliases for the three JSON payload shapes |

## Connection Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| Host | `127.0.0.1` | Localhost by default |
| Port | `12345` | MakeHuman's default socket port |

## Module-Level Types

These three are declared in `src/mpfb/types.py` rather than in this module, because the socket object entities read the same dicts back out. All three are deliberately aliases rather than `TypedDict`s: the values arrive from `json.loads()` as `Any`, and in the `SocketMeshInfo` case no single key set describes both of its producers.

| Name | Definition | Notes |
|------|------------|-------|
| `SocketMeshInfo` | `dict[str, Any]` | The description of one mesh, sent ahead of its geometry. Produced both by `get_body_mesh_info()` and as each entry of `get_proxies_info()`. Both carry `name` plus the `verticesShape`, `verticesTypeCode`, `facesShape`, `facesTypeCode`, `textureCoordsShape`, `textureCoordsTypeCode`, `faceUVMappingsShape` and `faceUVMappingsTypeCode` entries which say how to reshape the matching binary payload. The body additionally carries `filename`, `faceGroups` and `faceMask`; a proxy carries `type` and `uuid`, and reports its sizes as `numVertices`, `numFaces`, `numTextureCoords` and `numFaceUVMappings` instead of the four `*Shape` entries. |
| `SocketWeightInfo` | `dict[str, Any]` | The vertex weight index, sent ahead of the weights themselves. The only key read in MPFB is `weights`, a list with one entry per weighted bone carrying `bone` and `numVertices`. The order of that list is significant: it is what slices the two parallel binary payloads into per bone arrays. |
| `SocketSkeletonInfo` | `dict[str, Any]` | The skeleton of the currently loaded character. The keys read in MPFB are `name`, which is the string `"none"` when the character has no skeleton, and `bones`, a list of root bones each nesting its own `children`. This is not the same shape as `RigDefinition`, MPFB's own rig file format, which is flat and keyed by bone name. |

## Public API

### Connection Configuration

#### set_host(host)

Set the host address for socket connections.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `host` | `str` | — | The hostname or IP address |

**Returns:** None

---

#### set_port(port)

Set the port number for socket connections.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `port` | `int` | — | The port number |

**Returns:** None

---

### Directory Information

#### get_user_dir()

Get the MakeHuman user directory path.

**Returns:** `str | None` — The user data directory path as reported by MakeHuman, or `None` if the call carried no data.

Results are cached after the first call.

---

#### get_sys_dir()

Get the MakeHuman system directory path.

**Returns:** `str | None` — The system data directory path as reported by MakeHuman, or `None` if the call carried no data.

Results are cached after the first call.

---

### Body Mesh Data

#### get_body_mesh_info()

Get metadata about the body mesh.

**Returns:** `SocketMeshInfo | None` — Mesh metadata including the array shapes and type codes needed to read the binary calls below, plus `name`, `filename`, `faceGroups` and `faceMask`. `None` if the call carried no data. See Module-Level Types.

---

#### get_body_vertices()

Get body vertex positions as binary data.

**Returns:** `bytearray` — Raw binary data containing vertex coordinates.

The data is packed as 32-bit floats in x, y, z order for each vertex.

---

#### get_body_faces()

Get body face indices as binary data.

**Returns:** `bytearray` — Raw binary data containing face vertex indices.

---

#### get_body_texture_coords()

Get body texture coordinates as binary data.

**Returns:** `bytearray` — Raw binary data containing UV coordinates.

---

#### get_body_uv_mapping()

Get body UV face mappings as binary data.

**Returns:** `bytearray` — Raw binary data mapping faces to UV coordinates.

---

### Body Material Data

#### get_body_material_info()

Get material information for the body mesh.

**Returns:** `dict[str, Any] | None` — Material properties including texture paths, colors and shader settings, keyed by MHMAT key name. `None` if the call carried no data. This one has no shared alias: the shape belongs to the MHMAT format, which `MhMaterial` and the MHMAT key catalog describe properly.

---

### Skeleton Data

#### get_skeleton()

Get the skeleton definition.

**Returns:** `SocketSkeletonInfo | None` — The skeleton as `name` plus a `bones` list of root bones, each nesting its own `children`. `name` is the string `"none"` when the character has no skeleton. `None` if the call carried no data. See Module-Level Types.

---

### Body Weight Data

#### get_body_weight_info()

Get metadata about body vertex weights.

**Returns:** `SocketWeightInfo | None` — Weight metadata as a `weights` list, one entry per weighted bone, each carrying `bone` and `numVertices`. `None` if the call carried no data. See Module-Level Types.

---

#### get_body_weight_vertices()

Get the list of weighted vertices as binary data.

**Returns:** `bytearray` — Raw binary data containing vertex indices that have weights.

---

#### get_body_weights()

Get body vertex weights as binary data.

**Returns:** `bytearray` — Raw binary data containing weight values for each vertex-bone pair.

---

### Proxy (Asset) Data

All proxy methods except `get_proxies_info()` require a UUID parameter identifying the specific proxy asset. `get_proxies_info()` is how that UUID is obtained in the first place.

#### get_proxies_info()

Get information about all loaded proxy assets.

**Returns:** `list[SocketMeshInfo] | None` — A **list**, not a dict: one `SocketMeshInfo` per loaded proxy, each carrying its own `uuid` and `type`. `None` if the call carried no data. See Module-Level Types.

---

#### get_proxy_vertices(uuid)

Get proxy vertex positions as binary data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | The proxy's unique identifier |

**Returns:** `bytearray` — Raw binary vertex data.

---

#### get_proxy_faces(uuid)

Get proxy face indices as binary data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | The proxy's unique identifier |

**Returns:** `bytearray` — Raw binary face data.

---

#### get_proxy_texture_coords(uuid)

Get proxy texture coordinates as binary data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | The proxy's unique identifier |

**Returns:** `bytearray` — Raw binary UV data.

---

#### get_proxy_uv_mapping(uuid)

Get proxy UV face mappings as binary data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | The proxy's unique identifier |

**Returns:** `bytearray` — Raw binary UV mapping data.

---

#### get_proxy_weight_info(uuid)

Get metadata about proxy vertex weights.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | The proxy's unique identifier |

**Returns:** `SocketWeightInfo | None` — Weight metadata for the proxy, in the same shape as `get_body_weight_info()`. `None` if the call carried no data.

---

#### get_proxy_weight_vertices(uuid)

Get the list of weighted proxy vertices as binary data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | The proxy's unique identifier |

**Returns:** `bytearray` — Raw binary vertex index data.

---

#### get_proxy_weights(uuid)

Get proxy vertex weights as binary data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | The proxy's unique identifier |

**Returns:** `bytearray` — Raw binary weight data.

---

#### get_proxy_material_info(uuid)

Get material information for a proxy.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | The proxy's unique identifier |

**Returns:** `dict[str, Any] | None` — Material properties for the proxy, in the same shape as `get_body_material_info()`. `None` if the call carried no data.

---

## Examples

### Basic Connection Setup

```python
from mpfb.services.socketservice import SocketService

# Configure connection (if not using defaults)
SocketService.set_host("127.0.0.1")
SocketService.set_port(12345)

# Get directory information. Both can be None, see the Overview.
user_dir = SocketService.get_user_dir()
sys_dir = SocketService.get_sys_dir()
if user_dir is None or sys_dir is None:
    print("MakeHuman answered, but without directory information")
else:
    print(f"MakeHuman user dir: {user_dir}")
    print(f"MakeHuman system dir: {sys_dir}")
```

### Fetching Body Mesh Data

```python
from mpfb.services.socketservice import SocketService
import struct

# Get mesh metadata
mesh_info = SocketService.get_body_mesh_info()
if mesh_info is None:
    raise RuntimeError("MakeHuman did not return any mesh info")

# The shapes are what say how to read the binary payloads: [vertex count, 3] and
# [face count, columns per face]
print(f"Vertex shape: {mesh_info['verticesShape']}")
print(f"Face shape: {mesh_info['facesShape']}")

# Get vertex data as binary
vertex_data = SocketService.get_body_vertices()

# Parse binary data (3 floats per vertex)
num_floats = len(vertex_data) // 4
coords = struct.unpack(f'{num_floats}f', vertex_data)

# Reshape into vertices
vertices = []
for i in range(0, len(coords), 3):
    vertices.append((coords[i], coords[i+1], coords[i+2]))

print(f"Parsed {len(vertices)} vertices")
```

### Fetching Skeleton Data

```python
from mpfb.services.socketservice import SocketService

# Get skeleton definition
skeleton = SocketService.get_skeleton()

if skeleton is None:
    raise RuntimeError("MakeHuman did not return a skeleton")

if skeleton["name"] == "none":
    print("The character has no skeleton")
else:
    # "bones" is a list of root bones, each nesting its own "children" list,
    # so walking it means recursing rather than iterating a flat mapping
    def print_bone(bone_info, depth=0):
        head = bone_info.get("head")
        tail = bone_info.get("tail")
        print(f"{'  ' * depth}Bone '{bone_info['name']}': head={head}, tail={tail}")
        for child in bone_info["children"]:
            print_bone(child, depth + 1)

    for root_bone in skeleton["bones"]:
        print_bone(root_bone)
```

### Working with Proxies (Clothes, Hair, etc.)

```python
from mpfb.services.socketservice import SocketService

# Get all loaded proxies. This is a list of dicts, each carrying its own uuid.
proxies_info = SocketService.get_proxies_info()

for proxy_data in proxies_info or []:
    uuid = proxy_data["uuid"]
    proxy_name = proxy_data.get('name', 'Unknown')
    proxy_type = proxy_data.get('type', 'Unknown')
    print(f"Proxy: {proxy_name} ({proxy_type}) - UUID: {uuid}")

    # Get this proxy's vertices
    vertices = SocketService.get_proxy_vertices(uuid)
    print(f"  Vertex data size: {len(vertices)} bytes")

    # Get material info
    material = SocketService.get_proxy_material_info(uuid)
    print(f"  Material: {(material or {}).get('name', 'default')}")
```

### Fetching Weight Data

```python
from mpfb.services.socketservice import SocketService
import struct

# Get weight metadata. "weights" holds one entry per weighted bone, in the
# order the two binary payloads below are sliced by.
weight_info = SocketService.get_body_weight_info()
if weight_info is None:
    raise RuntimeError("MakeHuman did not return any weight info")
for entry in weight_info["weights"]:
    print(f"Bone {entry['bone']} weights {entry['numVertices']} vertices")

# Get the actual weights
weight_vertices = SocketService.get_body_weight_vertices()
weights = SocketService.get_body_weights()

# Parse and process weight data...
```

### Complete Import Workflow

```python
from mpfb.services.socketservice import SocketService
from mpfb.services.meshservice import MeshService
import struct

def import_from_makehuman():
    """Import the current MakeHuman character."""

    # Get mesh info
    mesh_info = SocketService.get_body_mesh_info()
    if mesh_info is None:
        raise RuntimeError("MakeHuman did not return any mesh info")

    # Get vertex positions
    vert_data = SocketService.get_body_vertices()
    num_verts = len(vert_data) // 12  # 3 floats * 4 bytes
    vert_coords = struct.unpack(f'{num_verts * 3}f', vert_data)

    vertices = []
    for i in range(0, len(vert_coords), 3):
        vertices.append((
            vert_coords[i],
            vert_coords[i + 1],
            vert_coords[i + 2]
        ))

    # Get face data
    face_data = SocketService.get_body_faces()
    # Parse face data...

    # Create the mesh object
    mesh_obj = MeshService.create_mesh_object(
        vertices, [], faces,  # faces parsed from face_data
        name="ImportedHuman"
    )

    # Get and apply skeleton
    skeleton = SocketService.get_skeleton()
    # Create armature from skeleton data...

    # Get and apply materials
    material_info = SocketService.get_body_material_info()
    # Create materials...

    # Import proxies. get_proxies_info returns a list, so the uuid comes out of
    # each entry rather than being the key.
    proxies = SocketService.get_proxies_info()
    for proxy_info in proxies or []:
        uuid = proxy_info["uuid"]
        # Import each proxy...

    return mesh_obj
```

### Error Handling

```python
from mpfb.services.socketservice import SocketService
import asyncio

def safe_fetch():
    """Fetch with error handling."""
    try:
        mesh_info = SocketService.get_body_mesh_info()
        if mesh_info is None:
            # MakeHuman answered, but the call carried no data. The reply's error
            # field says why, and SocketService does not look at it.
            print("MakeHuman returned no mesh info")
            return None
        return mesh_info
    except ConnectionRefusedError:
        print("Could not connect to MakeHuman. Is it running with socket enabled?")
        return None
    except asyncio.TimeoutError:
        print("Connection timed out")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

result = safe_fetch()
if result:
    print("Successfully fetched mesh info")
```
