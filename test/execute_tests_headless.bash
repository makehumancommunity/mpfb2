#!/usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

rm -rf coverage
rm .coverage

if [ -z "$BLENDER_EXE" ]; then
  echo "Must set the BLENDER_EXE environment variable to point at the blender executable"
else
  $BLENDER_EXE -b $SCRIPT_DIR/testdata/test_scene.blend -P $SCRIPT_DIR/test_headless.py
fi

