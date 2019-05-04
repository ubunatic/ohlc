# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Generic Twine Makefile
# ----------------------
# Contains twine targets for publishing a package to PyPi.
# Copy this your project and use it via `make -f twine.mk`.

.PHONY: help sign test-publish publish
PACKAGE := $(shell basename $(CURDIR))
PIP     := pip3

help:
	# Usage:
	#     make -f twine.mk TARGET
	# Targets:
	#     sign          sing python wheels
	#     test-publish  publish to testpypi
	#     punlish       publish to pypi
	# Variables:
	#     WHEELS        python wheels to publish (defaults to all whl-files in ./dist)
	#     PACKAGE       name of the package at pypi
	#     PIP           path to the pip binary
	#
	# Defaults:
	#     WHEELS:       $(WHEELS)
	#     PACKAGE:      $(PACKAGE)
	#     PIP:          $(PIP) 

sign:
	# sign the dist with your gpg key
	gpg --detach-sign -a dist/*.whl

test-publish:
	# uploading to testpypi (requires valid ~/.pypirc)
	twine upload --repository testpypi dist/*

test-install:
	$(PIP) install --user --index-url https://test.pypi.org/simple/ $(PACKAGE)

WHEELS = $(shell find dist -name '$(PKG)*.whl')
publish: sign
	# uploading to pypi (requires pypi account)
	# wheel: $(WHEEL)
	@read -p "start upload (y/N)? " key && test "$$key" = "y"
	twine upload --repository pypi $(WHEELS)

