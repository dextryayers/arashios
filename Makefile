SHELL := /bin/bash
EDITION ?= cinnamon
ARCH ?= amd64
VERSION ?= $(shell . ./versions.env && printf '%s' "$$ARASHIOS_VERSION")
JOBS ?= $(shell nproc)
ISO ?= $(firstword $(wildcard out/*.iso))
BOOT_MODE ?= uefi

.PHONY: help env env-strict tokens brand-assets theme theme-check desktop-check \
        package package-check design config config-matrix build verify test smoke lint clean distclean \
        toolstack toolstack-check wordlists licenses toolchain-lock toolchain-check coding-check \
        daily-check installer-check package-audit \
        packages repo repo-check sbom hardening-check compliance-check \
        vuln-scan reproducibility boot-matrix smoke-suite upgrade-check

help:
	@printf '%s\n' \
	  'make env' \
	  'make tokens' \
	  'make brand-assets' \
	  'make theme' \
	  'make theme-check' \
	  'make desktop-check' \
	  'make package' \
	  'make package-check' \
	  'make config EDITION=xfce ARCH=amd64' \
	  'make config-matrix' \
	  'make build EDITION=cinnamon ARCH=amd64' \
	  'make build EDITION=lxqt ARCH=i386 JOBS=8' \
	  'make verify ISO=out/ArashiOS-amd64-V1.10.21.iso' \
	  'make test ISO=out/ArashiOS-amd64-V1.10.21.iso BOOT_MODE=uefi' \
	  'make smoke            # di sesi live' \
	  'make lint' \
	  'make clean'

tokens:
	./scripts/generate-tokens.py

brand-assets:
	./scripts/generate-brand-assets.py

theme: tokens brand-assets
	./scripts/generate-theme.py

theme-check:
	./tests/theme.sh

desktop-check:
	./tests/desktop-matrix.sh

package: theme
	./scripts/build-branding-package.sh

package-check:
	./tests/branding-package.sh

design: theme package

toolstack:
	./scripts/generate-toolstack.py
	./scripts/generate-toolchain.py

toolstack-check:
	./tests/toolstack.sh

wordlists:
	./scripts/check-wordlists.py --update

licenses:
	./scripts/check-licenses.py --update

toolchain-lock:
	./scripts/refresh-toolchain-lock.py --cache $(HOME)/.cache/arashios/vendor

toolchain-check:
	./scripts/generate-toolchain.py --check
	./scripts/refresh-toolchain-lock.py --check

coding-check:
	./tests/coding.sh

daily-check:
	./tests/daily.sh

installer-check:
	./tests/installer.sh

package-audit:
	./scripts/check-packages-bookworm.py --index-dir $(INDEX_DIR) --fetch

packages:
	./scripts/build-branding-package.sh
	python3 ./scripts/build-packages.py --all

repo: packages
	./scripts/generate-repo-key.sh
	python3 ./scripts/build-repo.py --packages build/packages --output repo/public --sign

repo-check:
	python3 ./scripts/check-packages.py
	python3 ./scripts/snapshot-manifest.py --check
	./tests/repo-offline.sh

sbom:
	python3 ./scripts/generate-sbom.py --output build/arashios.sbom.json
	python3 ./scripts/check-sbom.py build/arashios.sbom.json

hardening-check:
	python3 ./scripts/check-hardening.py --config

compliance-check:
	python3 ./scripts/check-compliance.py --output build/compliance-report.json

vuln-scan:
	./scripts/scan-vulnerabilities.sh --output build/vulnerability-report.json

reproducibility:
	./scripts/check-reproducibility.sh

boot-matrix:
	./tests/boot-matrix.sh

smoke-suite:
	./tests/smoke-suite.sh --output build/smoke-report.json

upgrade-check:
	./tests/upgrade-path.sh

env:
	./scripts/check-env.sh

env-strict:
	./scripts/check-env.sh --strict

config:
	./build.sh --edition $(EDITION) --arch $(ARCH) --version $(VERSION) --dry-run

config-matrix:
	./tests/config-matrix.sh

build:
	./build.sh --edition $(EDITION) --arch $(ARCH) --version $(VERSION) --jobs $(JOBS)

verify:
	@test -n "$(ISO)" || { printf 'ERROR: tidak ada ISO. Set ISO=out/file.iso\n' >&2; exit 1; }
	./tests/verify-artifact.sh "$(ISO)"

test: verify
	./tests/qemu-boot.sh "$(ISO)" $(BOOT_MODE) 120

smoke:
	./tests/smoke.sh

lint: theme packages repo
	bash -n build.sh
	bash -n scripts/*.sh
	bash -n tests/*.sh
	python3 -m py_compile scripts/*.py
	shellcheck -x build.sh scripts/*.sh tests/*.sh
	./scripts/check-docs.sh
	./scripts/check-traceability.py
	./scripts/validate-config.sh
	./tests/theme.sh
	./tests/desktop-matrix.sh
	./tests/branding-package.sh
	./tests/toolstack.sh
	./tests/coding.sh
	./tests/daily.sh
	./tests/installer.sh
	python3 ./scripts/check-packages.py
	python3 ./scripts/check-hardening.py --config
	python3 ./scripts/check-compliance.py
	./tests/repo-offline.sh

clean:
	rm -rf build out

distclean: clean
	rm -rf .toolchain
