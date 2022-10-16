"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "air_density",
            "sample_value": "1.0"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "altitude",
            "sample_value": "0.0"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7f64543a2b98>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "dust_density",
            "sample_value": "1.0"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "ground_albedo",
            "sample_value": "0.30000001192092896"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "ozone_density",
            "sample_value": "1.0"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "sky_type",
            "sample_value": "NISHITA"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "sun_direction",
            "sample_value": "<Vector (0.0000, 0.0000, 1.0000)>"
        },
        {
            "allowed_values": [],
            "class": "bool",
            "name": "sun_disc",
            "sample_value": "True"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "sun_elevation",
            "sample_value": "0.2617993950843811"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "sun_intensity",
            "sample_value": "1.0"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "sun_rotation",
            "sample_value": "0.0"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "sun_size",
            "sample_value": "0.009512044489383698"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7f64543a2b08>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "turbidity",
            "sample_value": "2.200000047683716"
        }
    ],
    "class": "ShaderNodeTexSky",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        }
    ],
    "label": "Sky Texture",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeTexSky(self, name=None, color=None, label=None, x=None, y=None, air_density=None, altitude=None, color_mapping=None, dust_density=None, ground_albedo=None, ozone_density=None, sky_type=None, sun_direction=None, sun_disc=None, sun_elevation=None, sun_intensity=None, sun_rotation=None, sun_size=None, texture_mapping=None, turbidity=None, Vector=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexSky"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["air_density"] = air_density
    node_def["attributes"]["altitude"] = altitude
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["dust_density"] = dust_density
    node_def["attributes"]["ground_albedo"] = ground_albedo
    node_def["attributes"]["ozone_density"] = ozone_density
    node_def["attributes"]["sky_type"] = sky_type
    node_def["attributes"]["sun_direction"] = sun_direction
    node_def["attributes"]["sun_disc"] = sun_disc
    node_def["attributes"]["sun_elevation"] = sun_elevation
    node_def["attributes"]["sun_intensity"] = sun_intensity
    node_def["attributes"]["sun_rotation"] = sun_rotation
    node_def["attributes"]["sun_size"] = sun_size
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["attributes"]["turbidity"] = turbidity
    node_def["inputs"]["Vector"] = Vector

    return self._create_node(node_def)
