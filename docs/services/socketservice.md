# SocketService

SocketService handles asynchronous communication with a separate MakeHuman socket server. It manages JSON and binary remote calls for retrieving mesh data, material information, skeleton data, and proxy asset information, with caching support.

## Source

`src/mpfb/services/socketservice.py`

## Dependencies

- `LogService` — logging
- `JsonCall` — JSON-based remote call serialization

## Public API

### set_host(host)

Set the host address for socket connections.

### set_port(port)

Set the port number for socket connections.

### get_user_dir()

Get the user directory path from the MakeHuman server (cached).

### get_sys_dir()

Get the system directory path from the MakeHuman server (cached).

### get_body_mesh_info()

Get body mesh metadata from the server.

### get_body_vertices()

Get body vertices as binary data from the server.

### get_body_faces()

Get body face indices as binary data from the server.

### get_body_texture_coords()

Get body texture coordinates as binary data from the server.

### get_body_uv_mapping()

Get body UV mappings as binary data from the server.

### get_body_material_info()

Get body material information from the server.

### get_skeleton()

Get the skeleton definition from the server.

### get_body_weight_info()

Get body weight metadata from the server.

### get_body_weight_vertices()

Get body weight vertex list as binary data from the server.

### get_body_weights()

Get body weights as binary data from the server.

### get_proxies_info()

Get proxies metadata from the server.

### get_proxy_vertices(uuid)

Get proxy vertices for the given UUID as binary data.

### get_proxy_faces(uuid)

Get proxy face indices for the given UUID as binary data.

### get_proxy_texture_coords(uuid)

Get proxy texture coordinates for the given UUID as binary data.

### get_proxy_uv_mapping(uuid)

Get proxy UV mappings for the given UUID as binary data.

### get_proxy_weight_info(uuid)

Get proxy weight metadata for the given UUID.

### get_proxy_weight_vertices(uuid)

Get proxy weight vertex list for the given UUID as binary data.

### get_proxy_weights(uuid)

Get proxy weights for the given UUID as binary data.

### get_proxy_material_info(uuid)

Get proxy material information for the given UUID.

## Example

```python
from mpfb.services.socketservice import SocketService

SocketService.set_host("127.0.0.1")
SocketService.set_port(12345)
mesh_info = SocketService.get_body_mesh_info()
vertices = SocketService.get_body_vertices()
```
