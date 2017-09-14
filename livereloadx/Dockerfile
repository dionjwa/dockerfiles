# Description:
#
# Livereload server https://github.com/nitoyon/livereloadx
#

FROM node:6.11-alpine
MAINTAINER dion@transition9.com

RUN apk add --no-cache make gcc g++ python linux-headers udev && \
	npm install -g livereloadx && \
	apk del make gcc g++ python linux-headers udev
