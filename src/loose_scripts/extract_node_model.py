import bpy, pprint, os, json
from mpfb.services.locationservice import LocationService

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

alltypes = []

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
                
    alltypes.append(shadertype)
    

mpfb_entities = LocationService.get_mpfb_root("entities")
atoms = os.path.join(mpfb_entities, "nodemodel", "atoms")
init = os.path.join(atoms, "__init__.py")

with open(init, "w") as initfile:
    initfile.write("""
from mpfb.services.logservice import LogService
from mpfb.entities.nodemodel._internalnodemanager import InternalNodeManager
_LOG = LogService.get_logger("nodemodel.atoms")
_LOG.trace("initializing nodemodel atoms module")

class AtomNodeManager(InternalNodeManager):
    def __init__(self, node_tree):
        _LOG.trace("Constructing AtomNodeManager with node_tree", node_tree)
        InternalNodeManager.__init__(self, node_tree)
    
""")
    
    translations = dict()
    
    for shadertype in alltypes:
        class_name = shadertype["class"]
        class_lc = class_name.lower()
        class_filename = os.path.join(atoms, class_lc + ".py")
        
        with open(class_filename, "w") as class_file:
            class_file.write("\"\"\"\n")
            class_file.write(json.dumps(shadertype, indent=4, sort_keys=True))
            class_file.write("\"\"\"\n")
            class_file.write("def create" + class_name + "(self, name=None, color=None, label=None, x=None, y=None")
            for attribute in shadertype["attributes"]:
                name = attribute["name"].replace(".", "_").replace(" ", "_")
                if name != attribute["name"]:
                    translations[name] = attribute["name"]                    
                class_file.write(", " + name + "=None")

            for input in shadertype["inputs"]:
                name = input["identifier"].replace(".", "_").replace(" ", "_")
                if name != input["name"]:
                    translations[name] = input["identifier"]
                class_file.write(", " + name + "=None")
                
            class_file.write("):\n")
            class_file.write("    node_def = dict()\n")
            class_file.write("    node_def[\"attributes\"] = dict()\n")            
            class_file.write("    node_def[\"inputs\"] = dict()\n")                        
            class_file.write("    node_def[\"class\"] = \"" + class_name + "\"\n")
            class_file.write("    node_def[\"name\"] = name\n")         
            class_file.write("    node_def[\"color\"] = color\n")
            class_file.write("    node_def[\"label\"] = label\n")
            class_file.write("    node_def[\"x\"] = x\n")            
            class_file.write("    node_def[\"y\"] = y\n")

            for attribute in shadertype["attributes"]:
                name = attribute["name"].replace(".", "_").replace(" ", "_")
                original_name = name
                if name in translations:
                    original_name = translations[name]
                class_file.write("    node_def[\"attributes\"][\"" + original_name + "\"] = " + name + "\n")

            original_name = "MUPP"
            
            for input in shadertype["inputs"]:
                name = input["identifier"].replace(".", "_").replace(" ", "_")
                original_name = name
                if name in translations:
                    original_name = translations[name]
                class_file.write("    node_def[\"inputs\"][\"" + original_name + "\"] = " + name + "\n")
                
            if "Math" in class_name:
                print(translations)
                
            class_file.write("\n")
            class_file.write("    return self._create_node(node_def)\n")
                
        initfile.write("from ." + class_lc + " import create" + class_name + "\n")

    initfile.write("\n")
    
    for shadertype in alltypes:
        class_name = shadertype["class"]
        initfile.write("setattr(AtomNodeManager, \"create" + class_name + "\", create" + class_name + ")\n")
    
