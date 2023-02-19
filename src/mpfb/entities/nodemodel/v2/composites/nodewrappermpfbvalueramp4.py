import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbValueRamp4",
    "inputs": {
        "Input_0": {
            "name": "Value",
            "identifier": "Input_0",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_6": {
            "name": "ZeroStopValue",
            "identifier": "Input_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.9,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_8": {
            "name": "BetweenStop1Value",
            "identifier": "Input_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -3.402820018375656e+38,
            "max_value": 3.402820018375656e+38
        },
        "Input_11": {
            "name": "BetweenStop2Value",
            "identifier": "Input_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_13": {
            "name": "BetweenStop3Value",
            "identifier": "Input_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_7": {
            "name": "OneStopValue",
            "identifier": "Input_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_9": {
            "name": "BetweenStop1Position",
            "identifier": "Input_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.25,
            "min_value": 0.0001,
            "max_value": 0.9999
        },
        "Input_10": {
            "name": "BetweenStop2Position",
            "identifier": "Input_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.0001,
            "max_value": 0.9999
        },
        "Input_12": {
            "name": "BetweenStop3Position",
            "identifier": "Input_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.75,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        }
    },
    "outputs": {
        "Output_1": {
            "name": "Value",
            "identifier": "Output_1",
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
                -261.5234,
                580.6266
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
            "value": 301.2596
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Position",
            "to_node": "Map Range",
            "to_socket": "From Max"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Position",
            "to_node": "Map Range.001",
            "to_socket": "From Min"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ZeroStopValue",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Value",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.004",
            "from_socket": "Value",
            "to_node": "Math.005",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Position",
            "to_node": "Math.003",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.003",
            "from_socket": "Value",
            "to_node": "Math.005",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Map Range.001",
            "from_socket": "Result",
            "to_node": "Math.007",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.007",
            "from_socket": "Value",
            "to_node": "Math.008",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Value",
            "to_node": "Math.008",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Map Range.001",
            "from_socket": "Result",
            "to_node": "Math.009",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Position",
            "to_node": "Math.010",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.010",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.008",
            "from_socket": "Value",
            "to_node": "Math.011",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.009",
            "from_socket": "Value",
            "to_node": "Math.011",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.010",
            "from_socket": "Value",
            "to_node": "Math.012",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.011",
            "from_socket": "Value",
            "to_node": "Math.012",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Map Range.002",
            "from_socket": "Result",
            "to_node": "Math.014",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.014",
            "from_socket": "Value",
            "to_node": "Math.015",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range.002",
            "from_socket": "Result",
            "to_node": "Math.016",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.015",
            "from_socket": "Value",
            "to_node": "Math.017",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.016",
            "from_socket": "Value",
            "to_node": "Math.017",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.013",
            "from_socket": "Value",
            "to_node": "Math.018",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.017",
            "from_socket": "Value",
            "to_node": "Math.018",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Position",
            "to_node": "Map Range.001",
            "to_socket": "From Max"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Value",
            "to_node": "Math.009",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.013",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Position",
            "to_node": "Math.019",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.019",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.019",
            "from_socket": "Value",
            "to_node": "Math.020",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.012",
            "from_socket": "Value",
            "to_node": "Math.020",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.006",
            "from_socket": "Value",
            "to_node": "Math.021",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range.003",
            "from_socket": "Result",
            "to_node": "Math.022",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.022",
            "from_socket": "Value",
            "to_node": "Math.024",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.024",
            "from_socket": "Value",
            "to_node": "Math.026",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.023",
            "from_socket": "Value",
            "to_node": "Math.026",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.025",
            "from_socket": "Value",
            "to_node": "Math.027",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.026",
            "from_socket": "Value",
            "to_node": "Math.027",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.028",
            "from_socket": "Value",
            "to_node": "Math.029",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.027",
            "from_socket": "Value",
            "to_node": "Math.029",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop3Position",
            "to_node": "Math.028",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Position",
            "to_node": "Math.025",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.028",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop3Position",
            "to_node": "Math.013",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop3Value",
            "to_node": "Math.023",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.025",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop3Value",
            "to_node": "Math.023",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Position",
            "to_node": "Map Range.003",
            "to_socket": "From Min"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop3Position",
            "to_node": "Map Range.003",
            "to_socket": "From Max"
        },
        {
            "from_node": "Math.005",
            "from_socket": "Value",
            "to_node": "Math.006",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.020",
            "from_socket": "Value",
            "to_node": "Math.006",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.029",
            "from_socket": "Value",
            "to_node": "Math.030",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.018",
            "from_socket": "Value",
            "to_node": "Math.030",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.030",
            "from_socket": "Value",
            "to_node": "Math.021",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Value",
            "to_node": "Math.024",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop3Position",
            "to_node": "Map Range.002",
            "to_socket": "From Min"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop3Value",
            "to_node": "Math.015",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "OneStopValue",
            "to_node": "Math.016",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.021",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "Value"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -599.2636,
                    747.069
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range",
            "name": "Map Range",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    113.8909,
                    314.1913
                ],
                "operation": "LESS_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.003",
            "name": "Math.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -274.0942,
                    795.8581
                ],
                "operation": "SUBTRACT"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 1.0
            },
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -87.1208,
                    615.9531
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.001",
            "name": "Math.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -88.2897,
                    441.0092
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.002",
            "name": "Math.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    112.5717,
                    516.6386
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.004",
            "name": "Math.004",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    363.9436,
                    418.6867
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.005",
            "name": "Math.005",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    148.5636,
                    -1319.6238
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.017",
            "name": "Math.017",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -44.0749,
                    -1276.7574
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.015",
            "name": "Math.015",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -50.2824,
                    -1457.7494
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.016",
            "name": "Math.016",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -746.5659,
                    -238.2999
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range.001",
            "name": "Map Range.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -498.6699,
                    -346.0144
                ],
                "operation": "SUBTRACT"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 1.0
            },
            "label": "Math.007",
            "name": "Math.007",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -214.6385,
                    -345.1062
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.009",
            "name": "Math.009",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -269.0199,
                    -124.9533
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.008",
            "name": "Math.008",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -40.0281,
                    -206.9806
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.011",
            "name": "Math.011",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    159.648,
                    -64.6493
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.012",
            "name": "Math.012",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    346.0753,
                    41.645
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.020",
            "name": "Math.020",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -685.4334,
                    -894.8586
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range.003",
            "name": "Map Range.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -437.5374,
                    -1002.5731
                ],
                "operation": "SUBTRACT"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 1.0
            },
            "label": "Math.022",
            "name": "Math.022",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -153.5061,
                    -1001.6649
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.023",
            "name": "Math.023",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -207.8875,
                    -781.512
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.024",
            "name": "Math.024",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -206.5688,
                    -585.937
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.025",
            "name": "Math.025",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    21.1044,
                    -863.5393
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.026",
            "name": "Math.026",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    220.7804,
                    -721.2079
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.027",
            "name": "Math.027",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    407.2078,
                    -614.9137
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.029",
            "name": "Math.029",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -265.5224,
                    68.4423
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.010",
            "name": "Math.010",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    148.0035,
                    109.2077
                ],
                "operation": "LESS_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.019",
            "name": "Math.019",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    206.957,
                    -545.1714
                ],
                "operation": "LESS_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.028",
            "name": "Math.028",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    890.0573,
                    18.0507
                ]
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.021",
            "name": "Math.021",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    635.6671,
                    283.4658
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.0
            },
            "label": "Math.006",
            "name": "Math.006",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    685.7808,
                    -531.6617
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.0
            },
            "label": "Math.030",
            "name": "Math.030",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    381.7966,
                    -1209.9266
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.018",
            "name": "Math.018",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    148.3318,
                    -1107.2898
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.013",
            "name": "Math.013",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -802.9893,
                    -1386.6675
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range.002",
            "name": "Map Range.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    1252.9828,
                    49.1209
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
                    -458.5217,
                    -1578.9181
                ],
                "operation": "SUBTRACT"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 1.0
            },
            "label": "Math.014",
            "name": "Math.014",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1205.736,
                    -213.1223
                ]
            },
            "class": "NodeGroupInput",
            "input_socket_values": {},
            "label": "Group Input",
            "name": "Group Input",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbValueRamp4(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1252.9828, 49.1209]
        nodes["Group Input"].location = [-1205.736, -213.1223]

        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [-599.2636, 747.069]})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [113.8909, 314.1913], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-274.0942, 795.8581], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-87.1208, 615.9531], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-88.2897, 441.0092], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [112.5717, 516.6386], "use_clamp": True})
        node("ShaderNodeMath", "Math.005", attribute_values={"location": [363.9436, 418.6867], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.017", attribute_values={"location": [148.5636, -1319.6238], "use_clamp": True})
        node("ShaderNodeMath", "Math.015", attribute_values={"location": [-44.0749, -1276.7574], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.016", attribute_values={"location": [-50.2824, -1457.7494], "operation": "MULTIPLY"})
        node("ShaderNodeMapRange", "Map Range.001", attribute_values={"location": [-746.5659, -238.2999]})
        node("ShaderNodeMath", "Math.007", attribute_values={"location": [-498.6699, -346.0144], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.009", attribute_values={"location": [-214.6385, -345.1062], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.008", attribute_values={"location": [-269.0199, -124.9533], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.011", attribute_values={"location": [-40.0281, -206.9806], "use_clamp": True})
        node("ShaderNodeMath", "Math.012", attribute_values={"location": [159.648, -64.6493], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.020", attribute_values={"location": [346.0753, 41.645], "operation": "MULTIPLY"})
        node("ShaderNodeMapRange", "Map Range.003", attribute_values={"location": [-685.4334, -894.8586]})
        node("ShaderNodeMath", "Math.022", attribute_values={"location": [-437.5374, -1002.5731], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.023", attribute_values={"location": [-153.5061, -1001.6649], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.024", attribute_values={"location": [-207.8875, -781.512], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.025", attribute_values={"location": [-206.5688, -585.937], "operation": "GREATER_THAN"})
        node("ShaderNodeMath", "Math.026", attribute_values={"location": [21.1044, -863.5393], "use_clamp": True})
        node("ShaderNodeMath", "Math.027", attribute_values={"location": [220.7804, -721.2079], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.029", attribute_values={"location": [407.2078, -614.9137], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.010", attribute_values={"location": [-265.5224, 68.4423], "operation": "GREATER_THAN"})
        node("ShaderNodeMath", "Math.019", attribute_values={"location": [148.0035, 109.2077], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "Math.028", attribute_values={"location": [206.957, -545.1714], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "Math.021", attribute_values={"location": [890.0573, 18.0507]})
        node("ShaderNodeMath", "Math.006", attribute_values={"location": [635.6671, 283.4658], "use_clamp": True}, input_socket_values={"Value_001": 0.0})
        node("ShaderNodeMath", "Math.030", attribute_values={"location": [685.7808, -531.6617], "use_clamp": True}, input_socket_values={"Value_001": 0.0})
        node("ShaderNodeMath", "Math.018", attribute_values={"location": [381.7966, -1209.9266], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.013", attribute_values={"location": [148.3318, -1107.2898], "operation": "GREATER_THAN"})
        node("ShaderNodeMapRange", "Map Range.002", attribute_values={"location": [-802.9893, -1386.6675]})
        node("ShaderNodeMath", "Math.014", attribute_values={"location": [-458.5217, -1578.9181], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})

        link("Group Input", "Value", "Map Range", "Value")
        link("Group Input", "BetweenStop1Position", "Map Range", "From Max")
        link("Group Input", "BetweenStop1Position", "Map Range.001", "From Min")
        link("Group Input", "Value", "Map Range.001", "Value")
        link("Group Input", "ZeroStopValue", "Math.001", "Value_001")
        link("Group Input", "BetweenStop1Value", "Math.002", "Value_001")
        link("Group Input", "Value", "Math.003", "Value")
        link("Group Input", "BetweenStop1Position", "Math.003", "Value_001")
        link("Group Input", "BetweenStop1Value", "Math.008", "Value_001")
        link("Group Input", "BetweenStop1Position", "Math.010", "Value_001")
        link("Group Input", "Value", "Math.010", "Value")
        link("Group Input", "BetweenStop2Position", "Map Range.001", "From Max")
        link("Group Input", "BetweenStop2Value", "Math.009", "Value")
        link("Group Input", "Value", "Map Range.002", "Value")
        link("Group Input", "Value", "Math.013", "Value")
        link("Group Input", "BetweenStop2Position", "Math.019", "Value_001")
        link("Group Input", "Value", "Math.019", "Value")
        link("Group Input", "BetweenStop3Position", "Math.028", "Value_001")
        link("Group Input", "BetweenStop2Position", "Math.025", "Value_001")
        link("Group Input", "Value", "Math.028", "Value")
        link("Group Input", "BetweenStop3Position", "Math.013", "Value_001")
        link("Group Input", "BetweenStop3Value", "Math.023", "Value")
        link("Group Input", "Value", "Math.025", "Value")
        link("Group Input", "BetweenStop3Value", "Math.023", "Value_001")
        link("Group Input", "Value", "Map Range.003", "Value")
        link("Group Input", "BetweenStop2Position", "Map Range.003", "From Min")
        link("Group Input", "BetweenStop3Position", "Map Range.003", "From Max")
        link("Group Input", "BetweenStop2Value", "Math.024", "Value_001")
        link("Group Input", "BetweenStop3Position", "Map Range.002", "From Min")
        link("Group Input", "BetweenStop3Value", "Math.015", "Value_001")
        link("Group Input", "OneStopValue", "Math.016", "Value")
        link("Map Range", "Result", "Math", "Value_001")
        link("Math", "Value", "Math.001", "Value")
        link("Map Range", "Result", "Math.002", "Value")
        link("Math.001", "Value", "Math.004", "Value")
        link("Math.002", "Value", "Math.004", "Value_001")
        link("Math.004", "Value", "Math.005", "Value")
        link("Math.003", "Value", "Math.005", "Value_001")
        link("Map Range.001", "Result", "Math.007", "Value_001")
        link("Math.007", "Value", "Math.008", "Value")
        link("Map Range.001", "Result", "Math.009", "Value_001")
        link("Math.008", "Value", "Math.011", "Value")
        link("Math.009", "Value", "Math.011", "Value_001")
        link("Math.010", "Value", "Math.012", "Value")
        link("Math.011", "Value", "Math.012", "Value_001")
        link("Map Range.002", "Result", "Math.014", "Value_001")
        link("Math.014", "Value", "Math.015", "Value")
        link("Map Range.002", "Result", "Math.016", "Value_001")
        link("Math.015", "Value", "Math.017", "Value")
        link("Math.016", "Value", "Math.017", "Value_001")
        link("Math.013", "Value", "Math.018", "Value")
        link("Math.017", "Value", "Math.018", "Value_001")
        link("Math.019", "Value", "Math.020", "Value")
        link("Math.012", "Value", "Math.020", "Value_001")
        link("Math.006", "Value", "Math.021", "Value")
        link("Map Range.003", "Result", "Math.022", "Value_001")
        link("Math.022", "Value", "Math.024", "Value")
        link("Math.024", "Value", "Math.026", "Value")
        link("Math.023", "Value", "Math.026", "Value_001")
        link("Math.025", "Value", "Math.027", "Value")
        link("Math.026", "Value", "Math.027", "Value_001")
        link("Math.028", "Value", "Math.029", "Value")
        link("Math.027", "Value", "Math.029", "Value_001")
        link("Math.005", "Value", "Math.006", "Value")
        link("Math.020", "Value", "Math.006", "Value_001")
        link("Math.029", "Value", "Math.030", "Value")
        link("Math.018", "Value", "Math.030", "Value_001")
        link("Math.030", "Value", "Math.021", "Value_001")
        link("Math.021", "Value", "Group Output", "Value")

NodeWrapperMpfbValueRamp4 = _NodeWrapperMpfbValueRamp4()
