# Description:
#
# Package haxe and chokidar-cli+nodemon in the same image so you can run haxe
# builds automatically triggered by code changes, and then run the server
#

FROM haxe:3.4.2-stretch
MAINTAINER dion@transition9.com

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
		apt-get install -y nodejs rsync && \
		npm install -g chokidar-cli nodemon && \
		rm -rf /var/lib/apt/lists/*

ENV SHELL=/bin/bash