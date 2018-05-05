# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for
# easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/vars.mk` and ´include make/project.mk´ in your `Makefile`.
# Now you can use `make vars`, `make pyclean`, and `make dev-install`.

# Targets
# -------
# vars:        print all relevant vars
# pyclean:     remove pyc and other cached files
# dev-install: directly use the current source as installation

.PHONY: vars pyclean dev-install

# Printing make vars can be helpful when testing multiple Python versions.
vars:
	# Make Variables
	# --------------
	# CURDIR    $(CURDIR)
	# PKG       $(PKG)
	# MAIN      $(MAIN)
	#
	# PY        $(PY)
	# PYTHON    $(PYTHON)
	# PIP       $(PIP)
	# WHEELTAG  $(WHEELTAG)
	#
	# SETUP_DIR $(SETUP_DIR)
	# SRC_FILES $(SRC_FILES)
	# PRJ_TESTS $(PRJ_TESTS)
	#
	# Python Versions
	# ---------------
	# python: $(shell python    --version 2>&1)
	# PYTHON: $(shell $(PYTHON) --version 2>&1)

pyclean:
	pyclean . || true  # try to use system pyclean if available
	find . -name '*.py[co]'    -delete
	find . -name '__pycache__' -delete

copy:
	test -n "$(TRG)"           # ensure the copy target is set
	mkdir $(TRG)/make          # create make dir in target dir
	cp make/*.mk $(TRG)/make/  # copy all mk files

clean: makepy-clean
makepy-clean: ; $(MAKEPY) clean

dists backport bumpversion install dev-install: ; $(MAKEPY) $@

