"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "clamp",
            "sample_value": "True"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "data_type",
            "sample_value": "FLOAT"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "interpolation_type",
            "sample_value": "LINEAR"
        }
    ],
    "class": "ShaderNodeMapRange",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 0,
            "name": "Value"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "From Min",
            "index": 1,
            "name": "From Min"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "From Max",
            "index": 2,
            "name": "From Max"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "To Min",
            "index": 3,
            "name": "To Min"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "To Max",
            "index": 4,
            "name": "To Max"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Steps",
            "index": 5,
            "name": "Steps"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 6,
            "name": "Vector"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "From_Min_FLOAT3",
            "index": 7,
            "name": "From Min"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "From_Max_FLOAT3",
            "index": 8,
            "name": "From Max"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "To_Min_FLOAT3",
            "index": 9,
            "name": "To Min"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "To_Max_FLOAT3",
            "index": 10,
            "name": "To Max"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Steps_FLOAT3",
            "index": 11,
            "name": "Steps"
        }
    ],
    "label": "Map Range",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Result",
            "index": 0,
            "list_as_argument": false,
            "name": "Result"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 1,
            "list_as_argument": false,
            "name": "Vector"
        }
    ]
}"""
def createShaderNodeMapRange(self, name=None, color=None, label=None, x=None, y=None, clamp=None, data_type=None, interpolation_type=None, Value=None, From_Min=None, From_Max=None, To_Min=None, To_Max=None, Steps=None, Vector=None, From_Min_FLOAT3=None, From_Max_FLOAT3=None, To_Min_FLOAT3=None, To_Max_FLOAT3=None, Steps_FLOAT3=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeMapRange"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["clamp"] = clamp
    node_def["attributes"]["data_type"] = data_type
    node_def["attributes"]["interpolation_type"] = interpolation_type
    node_def["inputs"]["Value"] = Value
    node_def["inputs"]["From Min"] = From_Min
    node_def["inputs"]["From Max"] = From_Max
    node_def["inputs"]["To Min"] = To_Min
    node_def["inputs"]["To Max"] = To_Max
    node_def["inputs"]["Steps"] = Steps
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["From_Min_FLOAT3"] = From_Min_FLOAT3
    node_def["inputs"]["From_Max_FLOAT3"] = From_Max_FLOAT3
    node_def["inputs"]["To_Min_FLOAT3"] = To_Min_FLOAT3
    node_def["inputs"]["To_Max_FLOAT3"] = To_Max_FLOAT3
    node_def["inputs"]["Steps_FLOAT3"] = Steps_FLOAT3

    return self._create_node(node_def)
