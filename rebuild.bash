#!/bin/bash

WD=`pwd`
rm dist/*
cd src
zip -r ../dist/mpfb2.zip mpfb README.md -x \*\*/__pycache__/\*
cd ../dist
INFO=last_build.txt
echo > $INFO "Build date:"
LANG=en date >> $INFO
echo >> $INFO 
echo >> $INFO "Commit hash:"
git rev-parse HEAD >> $INFO
echo >> $INFO
echo >> $INFO "MD5 Sum:"
md5sum mpfb2.zip >> $INFO
cd $WD

