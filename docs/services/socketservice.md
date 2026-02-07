# SocketService

## Overview

SocketService is one of the more ancient of the services, tracing its roots back to when the main purpose of MPFB was to interact with 
a running MakeHuman instance. It has little use beyond that purpose.

SocketService handles asynchronous communication with a separate MakeHuman socket server. It manages JSON and binary remote calls for retrieving mesh data, material information, skeleton data, and proxy asset information from a running MakeHuman instance.

Unlike most MPFB services which are static classes, SocketService is instantiated as a module-level singleton. This is because it maintains connection state (host, port) and a result cache across multiple calls.

The service uses Python's `asyncio` library for non-blocking network I/O. It supports two types of remote calls: **JSON calls** for structured data (mesh metadata, material info, skeleton definitions) and **binary calls** for large numeric data (vertex positions, face indices, weights). Binary transfers are significantly more efficient for bulk geometry data.

The socket protocol is defined by MakeHuman's socket server API. Each call sends a function name and optional parameters as JSON, and receives either a JSON response or raw binary data depending on the function. See [JsonCall](jsoncall.md) for details on the call format.

SocketService caches results for certain calls (like directory paths) to avoid repeated network round-trips for static information.

## Source

`src/mpfb/services/socketservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.socketservice")` |
| `JsonCall` | JSON-serializable function call model |

## Connection Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| Host | `127.0.0.1` | Localhost by default |
| Port | `12345` | MakeHuman's default socket port |

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

**Returns:** `str` — The user data directory path as reported by MakeHuman.

Results are cached after the first call.

---

#### get_sys_dir()

Get the MakeHuman system directory path.

**Returns:** `str` — The system data directory path as reported by MakeHuman.

Results are cached after the first call.

---

### Body Mesh Data

#### get_body_mesh_info()

Get metadata about the body mesh.

**Returns:** `dict` — Mesh metadata including vertex count, face count, and other properties.

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

**Returns:** `dict` — Material properties including texture paths, colors, and shader settings.

---

### Skeleton Data

#### get_skeleton()

Get the skeleton definition.

**Returns:** `dict` — Complete skeleton data including bone hierarchy, positions, and constraints.

---

### Body Weight Data

#### get_body_weight_info()

Get metadata about body vertex weights.

**Returns:** `dict` — Weight metadata including bone names and weight counts.

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

All proxy methods require a UUID parameter identifying the specific proxy asset.

#### get_proxies_info()

Get information about all loaded proxy assets.

**Returns:** `dict` — Dictionary of proxy metadata keyed by UUID.

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

**Returns:** `dict` — Weight metadata for the proxy.

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

**Returns:** `dict` — Material properties for the proxy.

---

## Examples

### Basic Connection Setup

```python
from mpfb.services.socketservice import SocketService

# Configure connection (if not using defaults)
SocketService.set_host("127.0.0.1")
SocketService.set_port(12345)

# Get directory information
user_dir = SocketService.get_user_dir()
sys_dir = SocketService.get_sys_dir()
print(f"MakeHuman user dir: {user_dir}")
print(f"MakeHuman system dir: {sys_dir}")
```

### Fetching Body Mesh Data

```python
from mpfb.services.socketservice import SocketService
import struct

# Get mesh metadata
mesh_info = SocketService.get_body_mesh_info()
print(f"Vertex count: {mesh_info.get('numVertices')}")
print(f"Face count: {mesh_info.get('numFaces')}")

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

# skeleton contains bone hierarchy and transforms
for bone_name, bone_data in skeleton.get('bones', {}).items():
    head = bone_data.get('head')
    tail = bone_data.get('tail')
    print(f"Bone '{bone_name}': head={head}, tail={tail}")
```

### Working with Proxies (Clothes, Hair, etc.)

```python
from mpfb.services.socketservice import SocketService

# Get all loaded proxies
proxies_info = SocketService.get_proxies_info()

for uuid, proxy_data in proxies_info.items():
    proxy_name = proxy_data.get('name', 'Unknown')
    proxy_type = proxy_data.get('type', 'Unknown')
    print(f"Proxy: {proxy_name} ({proxy_type}) - UUID: {uuid}")

    # Get this proxy's vertices
    vertices = SocketService.get_proxy_vertices(uuid)
    print(f"  Vertex data size: {len(vertices)} bytes")

    # Get material info
    material = SocketService.get_proxy_material_info(uuid)
    print(f"  Material: {material.get('name', 'default')}")
```

### Fetching Weight Data

```python
from mpfb.services.socketservice import SocketService
import struct

# Get weight metadata
weight_info = SocketService.get_body_weight_info()
bone_names = weight_info.get('bones', [])
print(f"Bones with weights: {bone_names}")

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

    # Import proxies
    proxies = SocketService.get_proxies_info()
    for uuid in proxies:
        # Import each proxy...
        pass

    return mesh_obj
```

### Error Handling

```python
from mpfb.services.socketservice import SocketService

def safe_fetch():
    """Fetch with error handling."""
    try:
        mesh_info = SocketService.get_body_mesh_info()
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
