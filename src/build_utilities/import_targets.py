#!/usr/bin/python3

from pathlib import Path
import os, sys, re, pprint, numpy, gzip, shutil, json, fnmatch
from numpy.polynomial.polyutils import mapparms

if not "TARGETS_DIR" in os.environ:
    print("Must set the TARGETS_DIR environment variable")
    sys.exit(1)

loc = Path(os.path.abspath(__file__))
parent = loc.parent.parent.absolute()

outdir = os.path.join(str(parent), "mpfb", "data", "targets")
imagedir = os.path.join(outdir, "_images") 

targets_dir = os.path.abspath(os.environ["TARGETS_DIR"])
    
for file in Path(targets_dir).rglob('*.target'):
     
    print("Reading " + str(file))
    with open(file, "r") as target_file:
        lines = target_file.readlines()
     
    stripped_target = ""
             
    for line in lines:
        line = str(line).strip()
        if line and not line.startswith("#"):            
            line = re.sub(r'\s+', " ", line) + "\n"
            stripped_target = stripped_target + line
     
    subpath = str(file.parent)
    subpath = subpath.replace(targets_dir, "")
 
    if not subpath.startswith("/"):
        subpath = "/" + subpath
    if not subpath.endswith("/"):
        subpath = subpath + "/"
 
    destdir = outdir + subpath
    os.makedirs(destdir, exist_ok=True)
 
    outfile = os.path.join(destdir, file.name + ".gz")
    print("Writing " + str(outfile))
    with gzip.open(outfile, "wb") as gzip_file:
        gzip_file.write(bytearray(stripped_target, 'utf8'))
         
    print()

for file in Path(targets_dir).rglob('*.png'):
     
    if not os.path.basename(file).startswith("r-"):
        print("Copying image: " + str(file))
        shutil.copy(file, os.path.join(imagedir, os.path.basename(file)))

# We'll rearrange the target categories in order to avoid categories with 
# a huge amount of targets

new_sub_dirs = ["arms", "legs", "feet", "hands"]

for dirname in new_sub_dirs:
    full_path = os.path.join(outdir, dirname)
    if os.path.exists(full_path):
        shutil.rmtree(full_path, ignore_errors=True)
    os.makedirs(full_path, exist_ok=True)

rearrangements = [
    ["armslegs", "*arm-*", "arms"],
    ["armslegs", "*leg-*", "legs"],
    ["armslegs", "*legs-*", "legs"],
    ["armslegs", "*foot-*", "feet"],
    ["armslegs", "*hand-*", "hands"],
    ["measure", "*arm-*", "arms"],
    ["measure", "*leg-*", "legs"],
    ["measure", "*knee-*", "legs"],
    ["measure", "*calf-*", "legs"],
    ["measure", "*thigh-*", "legs"],
    ["measure", "*ankle-*", "feet"],
    ["measure", "*foot-*", "feet"],
    ["measure", "*hand-*", "hands"],
    ["measure", "*wrist-*", "hands"],
    ["measure", "*neck-*", "neck"],
    ["measure", "*chest-*", "torso"],
    ["measure", "*bust-*", "torso"],
    ["measure", "*hips-*", "torso"],
    ["measure", "*waist*", "torso"],
    ["measure", "*shoulder-*", "torso"]         
    ]

for rearrangement in rearrangements:
    fromdir = rearrangement[0]
    pattern = rearrangement[1]
    todir = rearrangement[2]
    fullfrom = os.path.join(outdir, fromdir)
    fullto = os.path.join(outdir, todir)
    for file in os.listdir(fullfrom):
        if fnmatch.fnmatch(file, pattern):
            shutil.move(os.path.join(fullfrom, file), os.path.join(fullto, file))

target_list = dict()

def guess_category_name(target):
    guessed_name = None
    if target.endswith("-incr") or target.endswith("-decr"):
        guessed_name = target
        guessed_name = re.sub(r"-incr$", "", guessed_name)
        guessed_name = re.sub(r"-decr$", "", guessed_name)
        guessed_name = guessed_name + "-decr-incr"

    if target.endswith("-down") or target.endswith("-up"):
        guessed_name = target
        guessed_name = re.sub(r"-down$", "", guessed_name)
        guessed_name = re.sub(r"-up$", "", guessed_name)
        guessed_name = guessed_name + "-down-up"

    if target.endswith("-in") or target.endswith("-out"):
        guessed_name = target
        guessed_name = re.sub(r"-in$", "", guessed_name)
        guessed_name = re.sub(r"-out$", "", guessed_name)
        guessed_name = guessed_name + "-in-out"

    if target.endswith("-backward") or target.endswith("-forward"):
        guessed_name = target
        guessed_name = re.sub(r"-backward$", "", guessed_name)
        guessed_name = re.sub(r"-forward$", "", guessed_name)
        guessed_name = guessed_name + "-backward-forward"

    if target.endswith("-concave") or target.endswith("-convex"):
        guessed_name = target
        guessed_name = re.sub(r"-concave$", "", guessed_name)
        guessed_name = re.sub(r"-convex$", "", guessed_name)
        guessed_name = guessed_name + "-concave-convex"

    if target.endswith("-compress") or target.endswith("-uncompress"):
        guessed_name = target
        guessed_name = re.sub(r"-compress$", "", guessed_name)
        guessed_name = re.sub(r"-uncompress$", "", guessed_name)
        guessed_name = guessed_name + "-compress-uncompress"

    if "shape" in target:
        if target.endswith("-square") or target.endswith("-round"):
            guessed_name = target
            guessed_name = re.sub(r"-square$", "", guessed_name)
            guessed_name = re.sub(r"-round$", "", guessed_name)
            guessed_name = guessed_name + "-square-round"

        if target.endswith("-pointed") or target.endswith("-triangle"):
            guessed_name = target
            guessed_name = re.sub(r"-pointed", "", guessed_name)
            guessed_name = re.sub(r"-triangle$", "", guessed_name)
            guessed_name = guessed_name + "-pointed-triangle"
        
    if guessed_name is None:
        guessed_name = target
        guessed_name = re.sub(r"^r-", "l-", guessed_name)
        
    if not guessed_name is None:
        guessed_name = re.sub(r"^r-", "l-", guessed_name)
        guessed_image_path = os.path.join(imagedir, guessed_name + ".png")
        if not os.path.exists(guessed_image_path):        
            print("WARNING: guessed target base has no image: " + guessed_image_path)            
        
    if not guessed_name is None:
        if guessed_name.startswith("r-") or guessed_name.startswith("l-"):
            guessed_name = re.sub(r"^l-", "", guessed_name)
            guessed_name = re.sub(r"^r-", "", guessed_name)
    
    return guessed_name

def excluded_dirname(dirname):
    for match in ["macrodetails", "_images", "asym", "expression", "armslegs"]:
        if dirname == match:
            return True
    return False

def populate_opposites_and_leftright(category):
    name = category["name"]
    opposites = [
        "decr-incr",
        "down-up",
        "in-out",
        "backward-forward",
        "concave-convex"
        "compress-uncompress",
        "square-round",
        "pointed-triangle"
        ]

    category["has_left_and_right"] = False
    
    for opposite in opposites:
        if name.endswith(opposite):
            parts = opposite.split("-", 2)
            negative = "-" + parts[0]
            positive = "-" + parts[1]
                        
            category["opposites"] = {
                "negative-unsided": "",
                "positive-unsided": "",
                "negative-left": "",
                "positive-left": "",
                "negative-right": "",
                "positive-right": ""
            }

            for target in category["targets"]:
                name = str(target)
                qualifier = "-unsided"
                if name.startswith("l-"):
                    qualifier = "-left"
                if name.startswith("r-"):
                    qualifier = "-right"
                if name.endswith(negative):
                    category["opposites"]["negative" + qualifier] = name
                if name.endswith(positive):
                    category["opposites"]["positive" + qualifier] = name

    for target in category["targets"]:
        if target.startswith("l-") or target.startswith("r-"):
            category["has_left_and_right"] = True


for directory in os.listdir(outdir):
    dirname = os.path.basename(directory)
    full_dir_path = os.path.join(outdir, directory) 
    if not excluded_dirname(dirname) and os.path.isdir(full_dir_path):
        section = dict()
        section["label"] = dirname
        section["include_per_default"] = True
        section["categories"] = []
        section["unsorted"] = []
        
        categories = dict()
        for target in os.listdir(full_dir_path):            
            if ".target.gz" in target and not target.startswith("female-"):
                target = target.replace(".target.gz", "")
                category_name = guess_category_name(target)
                if category_name is None:
                    section["unsorted"].append(target)
                    print("Target not in category: " + target)
                else:
                    if not category_name in categories:
                        categories[category_name] = dict()
                        categories[category_name]["name"] = category_name
                        categories[category_name]["label"] = category_name
                    category = categories[category_name]
                    if not "targets" in category:
                        category["targets"] = []
                    category["targets"].append(target)
        for category in categories:
            populate_opposites_and_leftright(categories[category])
            section["categories"].append(categories[category])
    
        target_list[dirname] = section
        
with open(os.path.join(outdir, "target.json"), "w") as json_file:
    json.dump(target_list, json_file, indent=4, sort_keys=True)




        