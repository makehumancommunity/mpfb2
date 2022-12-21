# Unit tests

This directory contains unit tests. 

## Running tests

The easiest way to execute the tests is from inside blender, using the unit tests button
on the developer panel. 

Alternatively, you can use the "execute\_tests\_headless.bash" script in the test
dir to run tests without opening the blender GUI. For this to work, you need to set
the path to the blender executable in the BLENDER\_EXE environment variable and 
be able to excute using linux-style path references.

Code coverage is only produced when running headless. A report is then written to
the tests/coverage directory.

## Prerequisites

Unit tests will only work if you run MPFB from source. Ie. realpath() of the mpfb addon 
directory must point to the src/mpfb dir in a source clone, for example via a symlink.

Further, you must use a blender which you have write permission to in order to install
dependencies. 

## Setting up

Before running unit tests the first time, you must install pytest in blender. To do
so, open [this script](./run_to_install_pytest.py) in the script tab inside blender
and run it. This will use pip to install the required dependencies. 

