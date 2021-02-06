#!/bin/bash

# Remove trailing whitespace
find src/mpfb -name "*.py" -exec "sed" "-i" "-e" 's/[ \t]*$//' {} ";"
