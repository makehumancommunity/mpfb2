#!/usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Clean previous coverage data (base file and all parallel files)
rm -rf "$SCRIPT_DIR/coverage"
rm -f "$SCRIPT_DIR/.coverage"
rm -f "$SCRIPT_DIR"/.coverage.*

# Activate coverage.py subprocess mode via the a1_coverage.pth already installed
# in Blender's Python. This starts coverage BEFORE Blender loads the mpfb addon.
export COVERAGE_PROCESS_START="$SCRIPT_DIR/.coveragerc"
# Pin the data file location so .coverage.* files land in test/
export COVERAGE_FILE="$SCRIPT_DIR/.coverage"

if [ -z "$BLENDER_EXE" ]; then
  echo "Must set the BLENDER_EXE environment variable to point at the blender executable"
else
  # cd to SCRIPT_DIR so relative paths in .coveragerc resolve correctly
  cd "$SCRIPT_DIR" && "$BLENDER_EXE" -b "$SCRIPT_DIR/testdata/test_scene.blend" -P "$SCRIPT_DIR/test_headless.py"

  # After Blender exits, atexit has saved .coverage.<host>.<pid>.pth
  # Combine all parallel files and generate the HTML report using Blender's Python
  BLENDER_PYTHON=$(find "$(dirname "$BLENDER_EXE")" -maxdepth 5 -name "python3*" -type f -executable 2>/dev/null | grep -E "bin/python3(\.[0-9]+)?$" | head -1)
  if [ -n "$BLENDER_PYTHON" ]; then
    cd "$SCRIPT_DIR"
    unset COVERAGE_PROCESS_START  # prevent coverage from starting again
    "$BLENDER_PYTHON" -m coverage combine
    "$BLENDER_PYTHON" -m coverage html
    echo "Coverage report written to test/coverage/"
  else
    echo "Warning: Could not find Blender's Python; skipping coverage report generation."
    echo "Run manually: python3 -m coverage combine && python3 -m coverage html"
  fi
fi
