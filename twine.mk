# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Generic Twine Makefile
# ----------------------
# Contains twine targets for publishing a package to PyPi.
# Copy this your project and use it via `make -f twine.mk`.

.PHONY: help sign wheel clean build test-wheel test-publish test-install publish
PY      := 3
_PIP    := pip$(PY)
_PYTHON := python$(PY)

_PACKAGE := $(shell $(_PYTHON) setup.py --name)
_VERSION := $(shell $(_PYTHON) setup.py --version)
_TAG     := $(shell date +%Y%m%d%H%M --utc)
# The development version is tagged with running build number using
# the current UTC time in the format YYYYmmddHHMM. It should be only
# used for testing. Do not upload this to pypi!

help:
	# Usage:
	#     make -f twine.mk TARGETS
	# Targets:
	#     sign          sing python wheels
	#     test-publish  publish to testpypi
	#     publish       publish to pypi
	# Variables:
	#     WHEELS        python wheels to publish (defaults to all whl-files in ./dist)
	#     PY            major python version to use
	#
	# Defaults:
	#     WHEELS:       $(WHEELS)
	#     PY:           $(PY)
	#     _PACKAGE:     $(_PACKAGE)
	#     _VERSION:     $(_VERSION)
	#     _TAG:         $(_TAG)

sign:
	# sign the dist with your gpg key
	gpg --detach-sign -a dist/*.whl

clean: ; $(MAKE) clean uninstall PY=$(PY)  # clean up code and binaries
build: ; $(MAKE) PY=$(PY)                  # run default targets
wheel: ; $(_PYTHON) setup.py bdist_wheel $(WHEEL_ARGS) && ls -l dist

test-wheel: WHEEL_ARGS := --build-number $(_TAG)
test-wheel: wheel

test-publish: clean build test-wheel
	# uploading to testpypi (requires valid ~/.pypirc)
	twine upload --repository testpypi dist/*

test-install: clean
	# installing from testpypi
	$(_PIP) install --user --upgrade --index-url https://test.pypi.org/simple/ $(_PACKAGE)
	# running the cli tests to ensure the package works
	$(MAKE) test-cli

WHEELS = $(shell find dist -name '$(PKG)*.whl')
publish: clean build wheel
	# uploading to pypi (requires pypi account)
	# wheels: $(WHEELS)
	@read -p "start upload (y/N)? " key && test "$$key" = "y"
	twine upload --repository pypi $(WHEELS)

