# This gets used in `-v` so it can be a docker volume name or a local path.
export LOCAL_VOL ?= rsync-dev

.PHONY: default
default: run

.PHONY: build
build:
	docker build -t puddl-ingress-rsync:dev .

.PHONY: bash
bash: build
	./bin/run bash

.PHONY: run
run: build
	env | grep VOL
	./bin/run
