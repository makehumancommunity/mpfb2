# This script searches through the source tree to locate all files which contain a panel
#
# The script will print a list of panels in the format path + \t + class name + \t + inherited classes 

import os, subprocess, io

script_location = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(script_location, "..", "..")
src_dir = os.path.abspath(os.path.join(root_dir, "src"))

os.chdir(root_dir)

child = subprocess.run(["grep", "-Ir", "MPFB_PT_", "src"],stdout=subprocess.PIPE) 

s = io.StringIO(child.stdout.decode("utf-8"))

operators = []

for line in s:
    parts = line.strip().split(":")
    if "__init__.py" not in parts[0] and "loose" not in parts[0] and "ClassManager" not in parts[1]:
        if "class" in parts[1]:
            outstr = parts[0] + "\t"
            classname = parts[1].split("(")[0]
            classname = classname.strip().replace("class ", "")
            outstr = outstr + classname
            inherited = parts[1].split("(")[1]
            inherited = inherited.strip().replace(")", "")
            outstr = outstr + "\t" + inherited
            print(outstr)
