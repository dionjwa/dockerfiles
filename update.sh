#!/bin/bash
if [ -z "$1" ]
then
  echo "Please supply your commit message"
  exit 1
fi
./gen.sh > README.md
git add .
git commit -m "$1"
git push origin master