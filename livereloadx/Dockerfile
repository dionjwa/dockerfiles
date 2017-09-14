# Description:
#
# Livereload server https://github.com/nitoyon/livereloadx
#

FROM node:8.4-alpine
MAINTAINER dion@transition9.com

RUN apk add --no-cache make gcc g++ python linux-headers udev && \
	npm install -g livereloadx && \
	apk del make gcc g++ python linux-headers udev
