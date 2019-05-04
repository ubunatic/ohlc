# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Generic Twine Makefile
# ----------------------
# Contains twine targets for publishing a package to PyPi.
# Copy this your project and use it via `make -f twine.mk`.

.PHONY: help sign test-publish publish

help:
	# Usage:
	#     make -f twine.mk TARGET
	# Targets:
	#     sign          sing python wheels
	#     test-publish  publish to testpypi
	#     punlish       publish to pypi
	# Variables:
	#     WHEEL         python wheels to publish (defaults to all whl-files in ./dist) 

sign:
	# sign the dist with your gpg key
	gpg --detach-sign -a dist/*.whl

test-publish:
	# uploading to testpypi (requires valid ~/.pypirc)
	twine upload --repository testpypi dist/*

WHEELS = $(shell find dist -name '$(PKG)*.whl')
publish: sign
	# uploading to pypi (requires pypi account)
	# wheel: $(WHEEL)
	@read -p "start upload (y/N)? " key && test "$$key" = "y"
	twine upload --repository pypi $(WHEELS)

