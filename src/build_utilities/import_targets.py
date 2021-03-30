#!/usr/bin/python3

from pathlib import Path
import os, sys, re, pprint, numpy, gzip

if not "TARGETS_DIR" in os.environ:
    print("Must set the TARGETS_DIR environment variable")
    sys.exit(1)

loc = Path(os.path.abspath(__file__))
parent = loc.parent.parent.absolute()

outdir = os.path.join(str(parent), "mpfb", "data", "targets")

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
    
