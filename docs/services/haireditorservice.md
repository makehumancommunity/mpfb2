# HairEditorService

HairEditorService provides utility functions for the MPFB hair editor. It manages hair and fur blend file paths, checks for installed hair assets, and provides shader link manipulation for hair materials within the Hair shader EEVEE node group.

## Source

`src/mpfb/services/haireditorservices.py`

## Dependencies

- `LogService` — logging
- `LocationService` — path resolution for blend files

## Public API

### get_hair_blend_path()

Get the file path to the hair blend file.

### get_fur_blend_path()

Get the file path to the fur blend file.

### is_hair_asset_installed()

Check if the hair asset blend file is installed.

### is_fur_asset_installed()

Check if the fur asset blend file is installed.

### join_texture_node_to_shader(img_node, shader_nodes, group_node, links, storage_key, store_links)

Join a texture node to the principled shaders in the Hair shader node group.

### restore_shader_links(img_node, shader_nodes, group_node, nodes, links, storage_key)

Restore previous color links to the principled shaders in the Hair shader node group.

## Example

```python
from mpfb.services.haireditorservices import HairEditorService

if HairEditorService.is_hair_asset_installed():
    hair_path = HairEditorService.get_hair_blend_path()
```
