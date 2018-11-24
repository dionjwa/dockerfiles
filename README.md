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
### ./fluent-probe

```
 Description:

 Minimal docker image for testing a connection to a fluent collecter.
 Usage:
 docker run --rm dionjwa/fluent-probe -h <FLUENT_HOST> -p <FLUENT_PORT> <fluent payload>


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


```
### ./livereloadx

```
 Description:

 Livereload server https://github.com/nitoyon/livereloadx


```
### ./make

```
 Description:

 Base alpine image for running make+docker build tasks
 Designed to provide the base image for all makefile
 commands so that you can provide a clean reproducible
 build environment on any system

 alpine 3.8

```
