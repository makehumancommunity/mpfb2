"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "cache_point_density",
            "sample_value": "<bpy_func ShaderNodeTexPointDensity.cache_point_density()>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "calc_point_density",
            "sample_value": "<bpy_func ShaderNodeTexPointDensity.calc_point_density()>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "calc_point_density_minmax",
            "sample_value": "<bpy_func ShaderNodeTexPointDensity.calc_point_density_minmax()>"
        },
        {
            "allowed_values": [],
            "class": "str",
            "name": "interpolation",
            "sample_value": "Linear"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "object",
            "sample_value": "None"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "particle_color_source",
            "sample_value": "PARTICLE_AGE"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "particle_system",
            "sample_value": "None"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "point_source",
            "sample_value": "PARTICLE_SYSTEM"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "radius",
            "sample_value": "0.30000001192092896"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "resolution",
            "sample_value": "100"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "space",
            "sample_value": "OBJECT"
        },
        {
            "allowed_values": [],
            "class": "str",
            "name": "vertex_attribute_name",
            "sample_value": ""
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "vertex_color_source",
            "sample_value": "VERTEX_COLOR"
        }
    ],
    "class": "ShaderNodeTexPointDensity",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        }
    ],
    "label": "Point Density",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Density",
            "index": 1,
            "name": "Density"
        }
    ]
}"""
def createShaderNodeTexPointDensity(self, name=None, color=None, label=None, x=None, y=None, cache_point_density=None, calc_point_density=None, calc_point_density_minmax=None, interpolation=None, object=None, particle_color_source=None, particle_system=None, point_source=None, radius=None, resolution=None, space=None, vertex_attribute_name=None, vertex_color_source=None, Vector=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexPointDensity"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["cache_point_density"] = cache_point_density
    node_def["attributes"]["calc_point_density"] = calc_point_density
    node_def["attributes"]["calc_point_density_minmax"] = calc_point_density_minmax
    node_def["attributes"]["interpolation"] = interpolation
    node_def["attributes"]["object"] = object
    node_def["attributes"]["particle_color_source"] = particle_color_source
    node_def["attributes"]["particle_system"] = particle_system
    node_def["attributes"]["point_source"] = point_source
    node_def["attributes"]["radius"] = radius
    node_def["attributes"]["resolution"] = resolution
    node_def["attributes"]["space"] = space
    node_def["attributes"]["vertex_attribute_name"] = vertex_attribute_name
    node_def["attributes"]["vertex_color_source"] = vertex_color_source
    node_def["inputs"]["Vector"] = Vector

    return self._create_node(node_def)
