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
git push origin
if [ $# -eq 2 ]
	then
		CURRENT_TAG=`git describe --abbrev=0 --tags`
		BASE_LIST=(`echo $CURRENT_TAG | tr '.' ' '`)
		V_MAJOR=${BASE_LIST[0]}
		V_MINOR=${BASE_LIST[1]}
		V_PATCH=${BASE_LIST[2]}
		V_MINOR=$((V_MINOR + 1))
		VERSION="$V_MAJOR.$V_MINOR.$V_PATCH"
		echo "New version tag: $VERSION"
		git tag "$VERSION"
		git push --tags origin
fi

