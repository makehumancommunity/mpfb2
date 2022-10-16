"""
{
    "attributes": [],
    "class": "ShaderNodeParticleInfo",
    "inputs": [],
    "label": "Particle Info",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Index",
            "index": 0,
            "name": "Index"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Random",
            "index": 1,
            "name": "Random"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Age",
            "index": 2,
            "name": "Age"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Lifetime",
            "index": 3,
            "name": "Lifetime"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Location",
            "index": 4,
            "name": "Location"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Size",
            "index": 5,
            "name": "Size"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Velocity",
            "index": 6,
            "name": "Velocity"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Angular Velocity",
            "index": 7,
            "name": "Angular Velocity"
        }
    ]
}"""
def createShaderNodeParticleInfo(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeParticleInfo"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
