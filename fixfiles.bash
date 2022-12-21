#!/bin/bash

# Remove trailing whitespace
find test -name "*.py" -exec "sed" "-i" "-e" 's/[ \t]*$//' {} ";"
find src/mpfb -name "*.py" -exec "sed" "-i" "-e" 's/[ \t]*$//' {} ";"
find src/mpfb -name "*.json" -exec "sed" "-i" "-e" 's/[ \t]*$//' {} ";"
find src/mpfb -name "*.json" -exec "sed" "-i" "-e" 's/[\x09\t]/    /g' {} ";"
