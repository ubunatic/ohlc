# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/makepy.mk` to include all mk files in your `Makefile`.
# Now you can use `make vars`, `make pyclean`, and `make dev-install`.

# This file provides targets that wrap the most common makepy commands, so that you
# can call makepy commands and custom targets together: `make <makepy-command> <custom-target>`.
# It also includes all other mk files so that you only need to `include make/makepy.mk`

.PHONY: dist backport dists install dev-install tox bumpversion version

include make/vars.mk

ifeq ($(WHEELTAG), py2)
TEST_DEP=backport
endif
test: $(TEST_DEP)

include make/project.mk
include make/tests.mk
include make/twine.mk

# passthrough makepy commands
MAKEPY_COMMANDS = dist backport dists install dev-install tox bumpversion version
$(MAKEPY_COMMANDS): ; $(MAKEPY) $@

# TODO: handle egg removal in makepy
uninstall: ; $(MAKEPY) uninstall && rm -rf *.egg-info
