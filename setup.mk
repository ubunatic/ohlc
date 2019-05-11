# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Generic Python Packaging Makefile
# ---------------------------------
# Contains setuptools and twine targets for building and publishing a package to PyPi.
# Copy this your project and use it via `make -f setup.mk`.

help:
	# Usage:
	#     make -f setup.mk TARGETS
	#
	# Main Targets:
	#     test-wheels   build and test python wheels
	#     test-publish  build and test wheels and publish to testpypi
	#     sign          GPG sign the python wheels
	#     publish       build wheels and publish to pypi
	#
	# Variables:
	#     WHEELS        python wheels to publish (defaults to all whl-files in ./dist)
	#     PY            major Python version to use
	#     TAG           additional build tag to use for the wheels
	#
	# Defaults:
	#     WHEELS:       $(WHEELS)
	#     PY:           $(PY)
	#     TAG:          $(TAG)

.PHONY: help sign wheels clean build install uninstall test test-wheels test-publish publish

# The wheels are initalized in-place when needed (assignement using `=` instead of `:=`) 
WHEELS = $(shell find dist -name '$(PKG)*.whl')

# The default build tag is a running build number using the current UTC time in the format YYYYmmddHHMM.
TAG     := $(shell date +%Y%m%d%H%M --utc)
PY      := 3
_PIP    := pip$(PY)
_PYTHON := python$(PY)

clean uninstall: ; $(MAKE) $@ PY=$(PY)  # clean up code and binaries
build: clean     ; $(MAKE) PY=$(PY)     # cleanup and run default targets

wheels: build
	$(_PYTHON) setup.py bdist_wheel --build-number $(TAG)
	ls -l dist  # showing wheels in dist

install: wheels ; $(_PIP) install --upgrade $(WHEELS)  # install local wheels
test:           ; $(MAKE) test-cli                     # run cli tests to test package


# Main Targets
# ------------
# The following targets are used from the command line during development.
# The other targets are mostly depending targets and need not to be used directly.
test-wheels: install test uninstall

test-publish: test-wheels
	# uploading to testpypi (requires valid ~/.pypirc)
	twine upload --repository testpypi dist/*

sign:
	# sign the wheels with your gpg key
	gpg --detach-sign -a dist/*.whl

publish: wheels
	# uploading to pypi (requires pypi account)
	# wheels: $(WHEELS)
	@read -p "start upload (y/N)? " key && test "$$key" = "y"
	twine upload --repository pypi $(WHEELS)

