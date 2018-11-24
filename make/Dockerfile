# Description:
#
# Base alpine image for running make+docker build tasks
# Designed to provide the base image for all makefile
# commands so that you can provide a clean reproducible
# build environment on any system
#

# alpine 3.8
FROM google/cloud-sdk:226.0.0-alpine

RUN apk --update add \
	bash \
	git \
	make \
	terraform \
	docker \
	python3

RUN pip3 install docker-compose


