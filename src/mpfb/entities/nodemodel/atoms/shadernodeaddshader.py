"""
{
    "attributes": [],
    "class": "ShaderNodeAddShader",
    "inputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Shader",
            "index": 0,
            "name": "Shader"
        },
        {
            "class": "NodeSocketShader",
            "identifier": "Shader_001",
            "index": 1,
            "name": "Shader"
        }
    ],
    "label": "Add Shader",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Shader",
            "index": 0,
            "name": "Shader"
        }
    ]
}"""
def createShaderNodeAddShader(self, name=None, color=None, label=None, x=None, y=None, Shader=None, Shader_001=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeAddShader"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Shader"] = Shader
    node_def["inputs"]["Shader_001"] = Shader_001

    return self._create_node(node_def)
