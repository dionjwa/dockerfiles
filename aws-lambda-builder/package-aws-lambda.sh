#!/usr/bin/env bash

if [ $# -eq 0 ]; then
	echo ""
    echo "    Package an AWS Lambda script with all node modules into a zip file"
    echo "    The packager runs in an AWS Linux docker container, so the node "
    echo "    modules are compiled for the correct architecture."
    echo ""
    echo "    -s/--src            The source folder of the lambda script"
    echo "    -d/--destination    The destination folder for the lambda zip file"
    echo ""
    exit 0
fi

# Use -gt 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use -gt 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it such
# as in the --default example).
# note: if this is set to -gt 0 the /etc/hosts part is not recognized ( may be a bug )
while [[ $# -gt 1 ]]
do
key="$1"

case $key in
    -s|--src)
    SRC="$2"
    shift # past argument
    ;;
    -d|--destination)
    DESTINATION="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done

set -e

cd ${SRC}

if [ ! -f package.json ]; then
	echo "Cannot create lambda package, 'package.json' file not found!"
	exit 1
fi
VERSION=`cat package.json | jq -r '. .version'`
LAMBDA_NAME=`cat package.json | jq -r '. .name'`
FILENAME=lambda-$LAMBDA_NAME-$VERSION.zip
npm install || exit 1
zip -r /destination/$FILENAME . || exit 1
