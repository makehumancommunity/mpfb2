# Run this in blender's script editor. You must have write permission to blender's python directory.
#
# Procedure inspired from https://b3d.interplanety.org/en/installing-python-packages-with-pip-in-blender-on-windows-10/

import subprocess
import sys
import os

python_exe = None

for root, dirs, files in os.walk(sys.prefix):
    for basename in files:
        if str(basename).startswith("python"):            
            if basename == "python" or basename == "python.exe":
                python_exe = os.path.join(root, basename)
                break
            if str(basename).startswith("python") and "bin" in root:               
                python_exe = os.path.join(root, basename)
                break

if not python_exe:
    raise IOError("Could not find python executable")

print("Python executable: " + python_exe)

subprocess.call([python_exe, '-m', 'ensurepip'])
subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])
subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pytest'])
subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pytest-cov'])

print("\nPytest should now be available")

