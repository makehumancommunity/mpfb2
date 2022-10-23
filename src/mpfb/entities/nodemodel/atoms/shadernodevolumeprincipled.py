"""
{
    "attributes": [],
    "class": "ShaderNodeVolumePrincipled",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketString",
            "identifier": "Color Attribute",
            "index": 1,
            "name": "Color Attribute"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Density",
            "index": 2,
            "name": "Density"
        },
        {
            "class": "NodeSocketString",
            "identifier": "Density Attribute",
            "index": 3,
            "name": "Density Attribute"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Anisotropy",
            "index": 4,
            "name": "Anisotropy"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Absorption Color",
            "index": 5,
            "name": "Absorption Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Emission Strength",
            "index": 6,
            "name": "Emission Strength"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Emission Color",
            "index": 7,
            "name": "Emission Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Blackbody Intensity",
            "index": 8,
            "name": "Blackbody Intensity"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Blackbody Tint",
            "index": 9,
            "name": "Blackbody Tint"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Temperature",
            "index": 10,
            "name": "Temperature"
        },
        {
            "class": "NodeSocketString",
            "identifier": "Temperature Attribute",
            "index": 11,
            "name": "Temperature Attribute"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 12,
            "name": "Weight"
        }
    ],
    "label": "Principled Volume",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Volume",
            "index": 0,
            "list_as_argument": false,
            "name": "Volume"
        }
    ]
}"""
def createShaderNodeVolumePrincipled(self, name=None, color=None, label=None, x=None, y=None, Color=None, Color_Attribute=None, Density=None, Density_Attribute=None, Anisotropy=None, Absorption_Color=None, Emission_Strength=None, Emission_Color=None, Blackbody_Intensity=None, Blackbody_Tint=None, Temperature=None, Temperature_Attribute=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeVolumePrincipled"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Color Attribute"] = Color_Attribute
    node_def["inputs"]["Density"] = Density
    node_def["inputs"]["Density Attribute"] = Density_Attribute
    node_def["inputs"]["Anisotropy"] = Anisotropy
    node_def["inputs"]["Absorption Color"] = Absorption_Color
    node_def["inputs"]["Emission Strength"] = Emission_Strength
    node_def["inputs"]["Emission Color"] = Emission_Color
    node_def["inputs"]["Blackbody Intensity"] = Blackbody_Intensity
    node_def["inputs"]["Blackbody Tint"] = Blackbody_Tint
    node_def["inputs"]["Temperature"] = Temperature
    node_def["inputs"]["Temperature Attribute"] = Temperature_Attribute
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
