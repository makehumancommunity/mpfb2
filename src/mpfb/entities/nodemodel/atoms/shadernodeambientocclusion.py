"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "inside",
            "sample_value": "False"
        },
        {
            "allowed_values": [],
            "class": "bool",
            "name": "only_local",
            "sample_value": "False"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "samples",
            "sample_value": "16"
        }
    ],
    "class": "ShaderNodeAmbientOcclusion",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Distance",
            "index": 1,
            "name": "Distance"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 2,
            "name": "Normal"
        }
    ],
    "label": "Ambient Occlusion",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "list_as_argument": false,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "AO",
            "index": 1,
            "list_as_argument": false,
            "name": "AO"
        }
    ]
}"""
def createShaderNodeAmbientOcclusion(self, name=None, color=None, label=None, x=None, y=None, inside=None, only_local=None, samples=None, Color=None, Distance=None, Normal=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeAmbientOcclusion"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["inside"] = inside
    node_def["attributes"]["only_local"] = only_local
    node_def["attributes"]["samples"] = samples
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Distance"] = Distance
    node_def["inputs"]["Normal"] = Normal

    return self._create_node(node_def)
