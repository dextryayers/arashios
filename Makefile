SHELL := /bin/bash
EDITION ?= cinnamon
ARCH ?= amd64
VERSION ?= $(shell . ./versions.env && printf '%s' "$$ARASHIOS_VERSION")
JOBS ?= $(shell nproc)
ISO ?= $(firstword $(wildcard out/*.iso))
BOOT_MODE ?= uefi

.PHONY: help tokens env env-strict config build verify test smoke lint clean distclean

help:
	@printf '%s\n' \
	  'make env' \
	  'make tokens' \
	  'make config EDITION=xfce ARCH=amd64' \
	  'make build EDITION=cinnamon ARCH=amd64' \
	  'make build EDITION=lxqt ARCH=i386 JOBS=8' \
	  'make verify ISO=out/ArashiOS-amd64-V1.10.21.iso' \
	  'make test ISO=out/ArashiOS-amd64-V1.10.21.iso BOOT_MODE=uefi' \
	  'make smoke' \
	  'make lint' \
	  'make clean'

tokens:
	./scripts/generate-tokens.py
	./scripts/generate-brand-assets.py

env:
	./scripts/check-env.sh

env-strict:
	./scripts/check-env.sh --strict

config:
	./build.sh --edition $(EDITION) --arch $(ARCH) --version $(VERSION) --dry-run

build:
	./build.sh --edition $(EDITION) --arch $(ARCH) --version $(VERSION) --jobs $(JOBS)

verify:
	@test -n "$(ISO)" || { printf 'ERROR: tidak ada ISO. Set ISO=out/file.iso\n' >&2; exit 1; }
	./tests/verify-artifact.sh "$(ISO)"

test: verify
	./tests/qemu-boot.sh "$(ISO)" $(BOOT_MODE) 120

smoke:
	./tests/smoke.sh

lint:
	bash -n build.sh
	bash -n scripts/*.sh
	bash -n tests/*.sh
	python3 -m py_compile scripts/*.py
	shellcheck -x build.sh scripts/*.sh tests/*.sh
	./scripts/check-docs.sh
	./scripts/check-traceability.py
	./scripts/validate-config.sh

clean:
	rm -rf build out

distclean: clean
	rm -rf .toolchain
