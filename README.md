# Docker images

Collection of useful Dockerfiles automatically built by dockerhub.

I've created some, and modified others.

Below is the overview generated from the Dockerfiles in the subdirectories.

Credit to https://github.com/cdrage/dockerfiles for the layout and scripts.


### ./aws-lambda-builder

```
 Description:

 To build aws nodejs lambdas you need a build environment
 to package up the scripts in a zip file for uploading
 to AWS. This image provides an AWS linux environment
 for this task.

 Usage:
 (Assumes the nodejs source and package.json is in the ./src folder and
  the artifacts should go in the ./destination folder)
 docker run --rm -ti -v $PWD/src:/src -v $PWD/src:/destination -w /src dionjwa/aws-lambda-builder -s /src -d /destination


```
### ./haxe-imports

```
 Description:

 Python script to fix/add haxe imports and package statements.
 Usage:
   docker run --rm -ti -v $PWD:/haxe dionjwa/haxe-imports


```
### ./haxe-watch

```
 Description:

 Package haxe and some useful nodejs build utils such as
  - chokidar-cli
  - nodemon
  - webpack
  - browserify
 in the same image so you can run haxe builds automatically triggered
 by code changes, and then run the server

Sometimes you want a port exposed (e.g. for reverse docker nginx proxying)

```
### ./livereloadx

```
 Description:

 Livereload server https://github.com/nitoyon/livereloadx


```
### ./node_modules

```
 Description:

 Docker image for just installing npm modules. Use this
 to create a docker volume with your npm modules that
 you can mount elsewhere


```
