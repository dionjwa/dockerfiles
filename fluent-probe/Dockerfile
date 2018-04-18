# Description:
#
# Minimal docker image for testing a connection to a fluent collecter.
# Usage:
# docker run --rm dionjwa/fluent-probe -h <FLUENT_HOST> -p <FLUENT_PORT> <fluent payload>
#

FROM node:8.11-alpine
MAINTAINER dion@transition9.com

RUN mkdir /app
WORKDIR /app

RUN npm i fluent-logger
RUN npm i commander

ADD test.js /app/test.js

ENTRYPOINT ["node", "test.js"]
