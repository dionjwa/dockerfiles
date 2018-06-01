SHELL=/bin/bash

export DOCKER_IMAGE     ?= test-image

.PHONY: image
image: image
	docker build -t ${DOCKER_IMAGE} .


.PHONY: test
test: develop-check
	bash -c 'sleep 8; open http://localhost:${DEV_SERVER_PORT}?WSPORT=8000' &
	DEV_SERVER_PORT=${DEV_SERVER_PORT} docker-compose up
