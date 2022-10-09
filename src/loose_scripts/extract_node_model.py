import bpy, pprint, json

nodeclasses = bpy.types.ShaderNode.__subclasses__()

nodenames = []

obj = bpy.context.object
nodes = obj.data.materials[0].node_tree.nodes

internal = []
blacklisted = []

internal = [
    '__doc__',
    '__module__',
    '__slots__',
    'bl_description',
    'bl_height_default',
    'bl_height_max',
    'bl_height_min',
    'bl_icon',
    'bl_idname',
    'bl_label',
    'bl_rna',
    'bl_static_type',
    'bl_width_default',
    'bl_width_max',
    'bl_width_min'
    ]
     
blacklisted = [
    'color',
    'dimensions',
    'draw_buttons',
    'draw_buttons_ext',
    'height',
    'hide',
    'input_template',
    'inputs',
    'internal_links',
    'is_registered_node_type',
    'label',
    'location',
    'mute',
    'name',
    'output_template',
    'outputs',
    'parent',
    'poll',
    'poll_instance',
    'rna_type',
    'select',
    'show_options',
    'show_preview',
    'show_texture',
    'socket_value_update',
    'type',
    'update',
    'use_custom_color',
    'width',
    'width_hidden'
    ]

exclude = []    

for n in nodeclasses:    
    nodeinstance = nodes.new(n.__name__)    
#    if n.__name__ == "ShaderNodeMath":
    #print(n.__name__)
    shadertype = dict()
    shadertype["class"] = n.__name__
    
    label = nodeinstance.name
    if "." in label:
        (label, junk) = label.split(".")
    shadertype["label"] = label
    shadertype["attributes"] = []
    shadertype["inputs"] = []
    shadertype["outputs"] = []    
    
    for item in dir(nodeinstance):
        if not item in internal and not item in blacklisted:
            attribute = dict()
            attribute["name"] = item
            attribute["class"] = "unknown"
            attribute["allowed_values"] = []
            value = getattr(nodeinstance, item)
            if type(value) is str:
                attribute["class"] = "str"
                if str(value).isupper():
                    attribute["class"] = "enum"
            if type(value) is bool:
                attribute["class"] = "bool"
            attribute["sample_value"] = str(value)
            shadertype["attributes"].append(attribute)            
    
    if hasattr(nodeinstance, "inputs") and nodeinstance.inputs:
        i = 0
        for input in nodeinstance.inputs:
            inputdef = dict()
            inputdef["name"] = input.name
            inputdef["index"] = i
            inputdef["identifier"] = input.identifier
            inputdef["class"] = str(input.__class__.__name__)
            shadertype["inputs"].append(inputdef)
            i = i + 1

    if hasattr(nodeinstance, "outputs") and nodeinstance.outputs:
        i = 0
        for output in nodeinstance.outputs:
            outputdef = dict()
            outputdef["name"] = output.name
            outputdef["index"] = i
            outputdef["identifier"] = output.identifier
            outputdef["class"] = str(output.__class__.__name__)
            shadertype["outputs"].append(outputdef)
            i = i + 1
            
    with open("/tmp/nodes/" + n.__name__ + ".json", "w") as json_file:
        json.dump(shadertype, json_file, indent=4, sort_keys=True)
        
    nodes.remove(nodeinstance)
