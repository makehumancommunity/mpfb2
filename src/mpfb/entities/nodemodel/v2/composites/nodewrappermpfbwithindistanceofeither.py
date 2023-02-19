import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbWithinDistanceOfEither",
    "inputs": {
        "Input_0": {
            "name": "Position",
            "identifier": "Input_0",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.5,
                0.5,
                0.0
            ]
        },
        "Input_1": {
            "name": "Coordinate1",
            "identifier": "Input_1",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.25,
                0.25,
                0.0
            ]
        },
        "Input_2": {
            "name": "Coordinate2",
            "identifier": "Input_2",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.75,
                0.75,
                0.0
            ]
        },
        "Input_3": {
            "name": "MaxDist",
            "identifier": "Input_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        }
    },
    "outputs": {
        "Output_4": {
            "name": "WithinDistance",
            "identifier": "Output_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_5": {
            "name": "ActualLeastDistance",
            "identifier": "Output_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        }
    },
    "attributes": {
        "color": {
            "name": "color",
            "class": "Color",
            "value": [
                0.608,
                0.608,
                0.608
            ]
        },
        "height": {
            "name": "height",
            "class": "float",
            "value": 100.0
        },
        "location": {
            "name": "location",
            "class": "Vector",
            "value": [
                -242.8965,
                530.403
            ]
        },
        "use_custom_color": {
            "name": "use_custom_color",
            "class": "bool",
            "value": false
        },
        "width": {
            "name": "width",
            "class": "float",
            "value": 248.0564
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "InRangeOfEither",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "WithinDistance"
        },
        {
            "from_node": "Distance2",
            "from_socket": "Value",
            "to_node": "DistanceMultInRange2",
            "to_socket": "Value"
        },
        {
            "from_node": "DistanceMultInRange1",
            "from_socket": "Value",
            "to_node": "LeastDistance",
            "to_socket": "Value"
        },
        {
            "from_node": "WithinRange1",
            "from_socket": "Value",
            "to_node": "InRangeOfEither",
            "to_socket": "Value"
        },
        {
            "from_node": "Distance1",
            "from_socket": "Value",
            "to_node": "DistanceMultInRange1",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Position",
            "to_node": "Distance1",
            "to_socket": "Vector"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Position",
            "to_node": "Distance2",
            "to_socket": "Vector"
        },
        {
            "from_node": "LeastDistance",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "ActualLeastDistance"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Coordinate1",
            "to_node": "Distance1",
            "to_socket": "Vector_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Coordinate2",
            "to_node": "Distance2",
            "to_socket": "Vector_001"
        },
        {
            "from_node": "Distance1",
            "from_socket": "Value",
            "to_node": "WithinRange1",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "MaxDist",
            "to_node": "WithinRange1",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "MaxDist",
            "to_node": "WithinRange2",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Distance2",
            "from_socket": "Value",
            "to_node": "WithinRange2",
            "to_socket": "Value"
        },
        {
            "from_node": "WithinRange1",
            "from_socket": "Value",
            "to_node": "DistanceMultInRange1",
            "to_socket": "Value_001"
        },
        {
            "from_node": "WithinRange2",
            "from_socket": "Value",
            "to_node": "DistanceMultInRange2",
            "to_socket": "Value_001"
        },
        {
            "from_node": "WithinRange2",
            "from_socket": "Value",
            "to_node": "InRangeOfEither",
            "to_socket": "Value_001"
        },
        {
            "from_node": "DistanceMultInRange2",
            "from_socket": "Value",
            "to_node": "LeastDistance",
            "to_socket": "Value_001"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -826.2397,
                    74.5913
                ]
            },
            "class": "NodeGroupInput",
            "input_socket_values": {},
            "label": "Group Input",
            "name": "Group Input",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    767.7954,
                    159.2626
                ]
            },
            "class": "NodeGroupOutput",
            "input_socket_values": {},
            "label": "Group Output",
            "name": "Group Output",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -150.688,
                    -6.303
                ],
                "operation": "LESS_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "WithinRange2",
            "name": "WithinRange2",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    101.513,
                    336.261
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "DistanceMultInRange1",
            "name": "DistanceMultInRange1",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    346.877,
                    275.289
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "InRangeOfEither",
            "name": "InRangeOfEither",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    345.329,
                    84.984
                ]
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "LeastDistance",
            "name": "LeastDistance",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -415.448,
                    -144.812
                ],
                "operation": "DISTANCE"
            },
            "class": "ShaderNodeVectorMath",
            "input_socket_values": {},
            "label": "Distance2",
            "name": "Distance2",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -435.557,
                    199.147
                ],
                "operation": "DISTANCE"
            },
            "class": "ShaderNodeVectorMath",
            "input_socket_values": {},
            "label": "Distance1",
            "name": "Distance1",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -153.909,
                    160.161
                ],
                "operation": "LESS_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "WithinRange1",
            "name": "WithinRange1",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    110.739,
                    -83.38
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "DistanceMultInRange2",
            "name": "DistanceMultInRange2",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbWithinDistanceOfEither(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Input"].location = [-826.2397, 74.5913]
        nodes["Group Output"].location = [767.7954, 159.2626]

        node("ShaderNodeMath", "WithinRange2", attribute_values={"location": [-150.688, -6.303], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "DistanceMultInRange1", attribute_values={"location": [101.513, 336.261], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "InRangeOfEither", attribute_values={"location": [346.877, 275.289], "use_clamp": True})
        node("ShaderNodeMath", "LeastDistance", attribute_values={"location": [345.329, 84.984]})
        node("ShaderNodeVectorMath", "Distance2", attribute_values={"location": [-415.448, -144.812], "operation": "DISTANCE"})
        node("ShaderNodeVectorMath", "Distance1", attribute_values={"location": [-435.557, 199.147], "operation": "DISTANCE"})
        node("ShaderNodeMath", "WithinRange1", attribute_values={"location": [-153.909, 160.161], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "DistanceMultInRange2", attribute_values={"location": [110.739, -83.38], "operation": "MULTIPLY"})

        link("Group Input", "Position", "Distance1", "Vector")
        link("Group Input", "Position", "Distance2", "Vector")
        link("Group Input", "Coordinate1", "Distance1", "Vector_001")
        link("Group Input", "Coordinate2", "Distance2", "Vector_001")
        link("Group Input", "MaxDist", "WithinRange1", "Value_001")
        link("Group Input", "MaxDist", "WithinRange2", "Value_001")
        link("Distance2", "Value", "DistanceMultInRange2", "Value")
        link("DistanceMultInRange1", "Value", "LeastDistance", "Value")
        link("WithinRange1", "Value", "InRangeOfEither", "Value")
        link("Distance1", "Value", "DistanceMultInRange1", "Value")
        link("Distance1", "Value", "WithinRange1", "Value")
        link("Distance2", "Value", "WithinRange2", "Value")
        link("WithinRange1", "Value", "DistanceMultInRange1", "Value_001")
        link("WithinRange2", "Value", "DistanceMultInRange2", "Value_001")
        link("WithinRange2", "Value", "InRangeOfEither", "Value_001")
        link("DistanceMultInRange2", "Value", "LeastDistance", "Value_001")
        link("InRangeOfEither", "Value", "Group Output", "WithinDistance")
        link("LeastDistance", "Value", "Group Output", "ActualLeastDistance")

NodeWrapperMpfbWithinDistanceOfEither = _NodeWrapperMpfbWithinDistanceOfEither()
