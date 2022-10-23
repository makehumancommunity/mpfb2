"""
{
    "attributes": [],
    "class": "ShaderNodeEeveeSpecular",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Base Color",
            "index": 0,
            "name": "Base Color"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Specular",
            "index": 1,
            "name": "Specular"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Roughness",
            "index": 2,
            "name": "Roughness"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Emissive Color",
            "index": 3,
            "name": "Emissive Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Transparency",
            "index": 4,
            "name": "Transparency"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 5,
            "name": "Normal"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Clear Coat",
            "index": 6,
            "name": "Clear Coat"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Clear Coat Roughness",
            "index": 7,
            "name": "Clear Coat Roughness"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Clear Coat Normal",
            "index": 8,
            "name": "Clear Coat Normal"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Ambient Occlusion",
            "index": 9,
            "name": "Ambient Occlusion"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 10,
            "name": "Weight"
        }
    ],
    "label": "Specular BSDF",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "BSDF",
            "index": 0,
            "list_as_argument": false,
            "name": "BSDF"
        }
    ]
}"""
def createShaderNodeEeveeSpecular(self, name=None, color=None, label=None, x=None, y=None, Base_Color=None, Specular=None, Roughness=None, Emissive_Color=None, Transparency=None, Normal=None, Clear_Coat=None, Clear_Coat_Roughness=None, Clear_Coat_Normal=None, Ambient_Occlusion=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeEeveeSpecular"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Base Color"] = Base_Color
    node_def["inputs"]["Specular"] = Specular
    node_def["inputs"]["Roughness"] = Roughness
    node_def["inputs"]["Emissive Color"] = Emissive_Color
    node_def["inputs"]["Transparency"] = Transparency
    node_def["inputs"]["Normal"] = Normal
    node_def["inputs"]["Clear Coat"] = Clear_Coat
    node_def["inputs"]["Clear Coat Roughness"] = Clear_Coat_Roughness
    node_def["inputs"]["Clear Coat Normal"] = Clear_Coat_Normal
    node_def["inputs"]["Ambient Occlusion"] = Ambient_Occlusion
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
