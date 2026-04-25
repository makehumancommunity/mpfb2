# This script scans all python files under src/mpfb and checks that every
# relative import actually resolves to an existing file on disk.

import os, re

script_location = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_location, "..", ".."))
mpfb_dir = os.path.join(root_dir, "src", "mpfb")

IMPORT_RE = re.compile(r'^\s*from\s+(\.+)([\w.]*)\s+import\s+')

def resolve(file_path, dots, module_path):
    base = os.path.dirname(file_path)
    for _ in range(len(dots) - 1):
        base = os.path.dirname(base)
    if module_path:
        return os.path.join(base, module_path.replace(".", os.sep))
    return base

errors_found = 0
for dirpath, _, filenames in os.walk(mpfb_dir):
    for filename in sorted(filenames):
        if not filename.endswith(".py"):
            continue
        full_path = os.path.join(dirpath, filename)
        with open(full_path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                m = IMPORT_RE.match(line)
                if not m:
                    continue
                dots, module_path = m.group(1), m.group(2)
                candidate = resolve(full_path, dots, module_path)
                if not (os.path.isfile(candidate + ".py") or
                        os.path.isfile(os.path.join(candidate, "__init__.py"))):
                    rel_file = os.path.relpath(full_path, root_dir)
                    rel_cand = os.path.relpath(candidate, root_dir)
                    print(f"FAULTY: {rel_file}:{lineno}")
                    print(f"  {line.rstrip()}")
                    print(f"  Resolved to: {rel_cand}  (not found)")
                    errors_found += 1

print(f"\n{errors_found} faulty import(s) found.")
