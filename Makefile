SHELL := /usr/bin/env bash
EDITION ?= cinnamon
ARCH ?= amd64
VERSION := $(shell . ./versions.env && printf '%s' "$$ARASHIOS_VERSION")
ISO := out/ArashiOS-$(ARCH)-$(VERSION).iso

.PHONY: help build test lint clean env

help:
	@printf '%s\n' \
	  'make build EDITION=cinnamon ARCH=amd64' \
	  'make build EDITION=xfce ARCH=amd64' \
	  'make build EDITION=lxqt ARCH=i386' \
	  'make test ISO=out/file.iso' \
	  'make lint' \
	  'make env' \
	  'make clean'

build:
	./build.sh --edition $(EDITION) --arch $(ARCH) --version $(VERSION)

lint:
	bash -n build.sh
	bash -n scripts/*.sh
	bash -n tests/*.sh
	./scripts/validate-config.sh

env:
	./scripts/check-env.sh

test:
	./tests/qemu-boot.sh $(ISO) uefi

clean:
	rm -rf build out
