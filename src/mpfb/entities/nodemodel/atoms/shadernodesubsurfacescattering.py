"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "falloff",
            "sample_value": "RANDOM_WALK"
        }
    ],
    "class": "ShaderNodeSubsurfaceScattering",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Scale",
            "index": 1,
            "name": "Scale"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Radius",
            "index": 2,
            "name": "Radius"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "IOR",
            "index": 3,
            "name": "IOR"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Anisotropy",
            "index": 4,
            "name": "Anisotropy"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 5,
            "name": "Normal"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 6,
            "name": "Weight"
        }
    ],
    "label": "Subsurface Scattering",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "BSSRDF",
            "index": 0,
            "list_as_argument": false,
            "name": "BSSRDF"
        }
    ]
}"""
def createShaderNodeSubsurfaceScattering(self, name=None, color=None, label=None, x=None, y=None, falloff=None, Color=None, Scale=None, Radius=None, IOR=None, Anisotropy=None, Normal=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeSubsurfaceScattering"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["falloff"] = falloff
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Scale"] = Scale
    node_def["inputs"]["Radius"] = Radius
    node_def["inputs"]["IOR"] = IOR
    node_def["inputs"]["Anisotropy"] = Anisotropy
    node_def["inputs"]["Normal"] = Normal
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
