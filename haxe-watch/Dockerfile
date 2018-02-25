# Description:
#
# Package haxe and some useful nodejs build utils such as
#  - chokidar-cli
#  - nodemon
#  - webpack
#  - browserify
# in the same image so you can run haxe builds automatically triggered
# by code changes, and then run the server
#

FROM haxe:3.4.4-stretch
MAINTAINER dion@transition9.com

ENV SHELL=/bin/bash

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
		apt-get install -y nodejs rsync jq curl make g++ gcc && \
		npm install -g chokidar-cli nodemon webpack browserify && \
		rm -rf /var/lib/apt/lists/*


#Sometimes you want a port exposed (e.g. for reverse docker nginx proxying)
EXPOSE 9000
ENV PORT 9000
