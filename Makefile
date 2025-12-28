ROOT_DIR:=$(realpath $(shell dirname $(firstword $(MAKEFILE_LIST))))

.ONESHELL:
SHELL = /bin/bash

venv: requirements.txt
	python -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt

.PHONY: format
format:
	source venv/bin/activate
	black -l 90 $(ROOT_DIR)

.PHONY: check
check:
	source venv/bin/activate
	ruff check $(ROOT_DIR)

.PHONY: run
run: venv
	source venv/bin/activate
	python main.py --comfy-addr $(COMFY_ADDR) --listen $(HOST_IP) --port $(HOST_PORT)

all: run
