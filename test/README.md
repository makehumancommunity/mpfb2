# Unit tests

This directory contains unit tests. These have to be run from inside blender, using
the unit tests button on the developer panel. 

## Prerequisites

Unit tests will only work if you run from source. Ie. realpath() of the mpfb addon 
directory must point to the src/mpfb dir in a source clone, for example via a symlink.

Further, you must use a blender which you have write permission to in order to install
dependencies. 

## Setting up

Before running unit tests the first time, you must install pytest in blender. To do
so, open [this script](./run_to_install_pytest.py) in the script tab inside blender
and run it. This will use pip to install the required dependencies. 

