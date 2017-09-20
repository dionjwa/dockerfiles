#!/bin/bash
#
if [ -z "$1" ]
then
	echo "Please supply your commit message"
	exit 1
fi
./gen.sh > README.md
git add .
git commit -m "$1"

if [ $# -eq 2 ]
then
	CURRENT_TAG=`git describe --abbrev=0 --tags`
	BASE_LIST=(`echo $CURRENT_TAG | tr '.' ' '`)
	echo "$BASE_LIST"
	V_MAJOR=${BASE_LIST[0]}
	V_MINOR=${BASE_LIST[1]}
	V_PATCH=${BASE_LIST[2]}
	echo "V_MAJOR=$V_MAJOR"
	echo "V_MINOR=$V_MINOR"
	echo "V_PATCH=$V_PATCH"
	V_MINOR=$((V_MINOR + 1))
	echo "V_MINOR=$V_MINOR"
	VERSION="$V_MAJOR.$V_MINOR.$V_PATCH"
	echo "git tag $VERSION"
	git tag "$VERSION"
fi

git push --tags origin