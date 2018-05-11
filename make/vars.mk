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

# This mk file defines the most common vars for building Python projects.
# Run `make PY=2` or `make PY=3` to setup vars for either Python 2 or 3.

# Using PYTHONPATH leads to unpredicted behavior.
unexport PYTHONPATH

# The default project name is the name of the current dir. All code usually
# resides in another subdir (package) with the same name as the project.
PKG  = $(notdir $(basename $(CURDIR)))
MAIN = $(PKG)

# main python vars, defining python and pip binaries
_GET_MAJOR = 'import sys; sys.stdout.write(str(sys.version_info.major) + "\n")'
_GET_MINOR = 'import sys; sys.stdout.write(str(sys.version_info.minor) + "\n")'
PY     := $(shell python -c $(_GET_MAJOR)).$(shell python -c $(_GET_MINOR))
PYTHON = python$(PY)
PIP    = $(PYTHON) -m pip
MAKEPY = $(PYTHON) -m makepy

# export and define setup vars, used for dist building
export WHEELTAG := py$(shell $(PYTHON) -c $(_GET_MAJOR))
ifeq ($(WHEELTAG), py2)
SETUP_DIR = backport
else
SETUP_DIR = $(CURDIR)
endif

# The default tests dir is 'tests'.
# Use PRJ_TESTS = other1 other2 in your Makefile to override.
PRJ_TESTS = $(wildcard ./tests)
# We use regard project files as source files to trigger rebuilds, etc.
PRJ_FILES = tox.ini setup.py setup.cfg project.cfg Makefile LICENSE.txt README.md
SRC_FILES = $(PKG) $(PRJ_TESTS) $(PRJ_FILES)

# utils and help vars
NOL       = 1>/dev/null  # mute stdout
NEL       = 2>/dev/null  # mute stderr
