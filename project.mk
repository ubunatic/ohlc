# Generic Project Makefile
# ========================
# Copy this file to each of python project to be able to test,
# build, and publish it easily.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include project.mk` in your `Makefile`.
# Then add your common targets, such as `test`, `docker-test`, etc.
# Now use `make`, `make test`, `make install`, etc.
# See each target for more details.	
#
# New Project Quickstart 
# ----------------------
# Just run `make clone PREFIX=path/to NEW_PRJ=new_project
# This will copy all important files to $(PREFIX)/$(NEW_PRJ)
# and try to replace all relevant old $(PRJ) strings with $(NEW_PRJ)
#
# Notes
# -----
# - All `_lower_case` vars are internal vars not supposed to be overwritten.
# - Try not to change this file to it your project's needs. Try to handle
#   all custom building in your main `Makefile`.
#

.PHONY: all test base-test clean install publish test-publish sign docker-test docker-base-test clone build

# The default project name is the name of the current dir
PRJ       := $(shell basename $(CURDIR))
PRJ_TESTS := $(shell if test -e tests; then echo tests; fi)
# All code should reside in another subdir with that name of the project
PRJ_TOOLS := setup.py project.mk
PRJ_FILES := setup.cfg project.cfg Makefile LICENSE.txt README.md
TP_FILES  := $(PRJ) $(PRJ_TESTS) $(PRJ_FILES) $(PRJ_TOOLS)
# All code is assumed to be written for Py3, for Py2 support we need to transpile it
DIST      := transpiled/dist

# you can override, e.g., PY=2 to test other python versions
PY          := $(shell python -c 'import sys; print(sys.version_info.major)')
PYTHON      := python$(PY)
PYTHON2     := $(shell which python2.7 $(NOL) $(NEL))
PIP         = $(PYTHON) -m pip
NOL         = 1>/dev/null
NEL         = 2>/dev/null
# The main module is a module with the name of the project in the project subdir
MAIN        ?= $(PRJ)
# Default tests include importing and running the module
CLI_TEST    = $(PYTHON) -m $(MAIN) -h >/dev/null
IMPORT_TEST = $(PYTHON) -c "import $(MAIN)"

INSTALL_BACKPORT := $(shell test -z $(PYTHON2) || echo install-backport)

export PYTHONPATH+=:.

all: clean test

# make test deend on base-test to trigger all tests
# when running `make test` (don't forget you write you own `test`!)
test: install-tools base-test

base-test: $(TP_FILES)
	# lint and test the project (PYTHONPATH = $(PYTHONPATH))
	pyclean .
	$(PYTHON) -m flake8
	$(PYTHON) -m pytest -s $(PRJ) $(PRJ_TESTS)
	$(CLI_TEST)
	$(IMPORT_TEST)

clean:
	pyclean .
	rm -rf .pytest_cache .cache dist build transpiled $(PRJ).egg-info

install-source: test
	# Directly install $(PRJ) in the local system. This will link your installation
	# to the code in this repo for quick and easy local development.
	$(PIP) install --user -e .
	#
	# source installation
	# -------------------
	$(PIP) show $(PRJ)

TP_WHL = $(shell find ./transpiled/dist -name '*.whl')
install-backport: build
	# install transpiled version using std pip (should wrrk with pip2 and pip3)
	pip2.7 uninstall -y $(PRJ)
	pip2.7 install --user --force-reinstall $(TP_WHL)
	bash -c 'cd / && $(PRJ) -h && $(PYTHON2) -m $(MAIN) -h' $(NOL)
	#
	# transpiled installation
	# -----------------------
	pip2.7 show $(PRJ)

install: install-source $(INSTALL_BACKPORT)

install-tools:
	# ensure tools are present
	@$(NIL) $(PIP) show pytest || $(PIP) install --user pytest
	@$(NIL) $(PIP) show flake8 || $(PIP) install --user flake8

build: transpiled

transpiled: $(TP_FILES)
	# copy all code to transpiled, try to convert it to Py2, and build the dist there
	mkdir -p transpiled
	cp -r $(TP_FILES) transpiled
	pasteurize -w --no-diff transpiled/$(PRJ)
	sed -i 's#\(ignore[ ]*=[ ]*.*\)#\1,F401#g' transpiled/setup.cfg
	$(MAKE) -C transpiled dist PY=2 DIST=dist PRJ=$(PRJ)
	ls $(DIST)

dist: test $(TP_FILES)
	# build the dist (should be called via transpiled)
	rm -f $@/*.whl $@/*.asc
	python3 setup.py bdist_wheel

sign: $(DIST)
	# sign the dist with your gpg key
	gpg --detach-sign -a $(DIST)/*.whl

test-publish: test build
	# upload to testpypi (need valid ~/.pypirc)
	twine upload --repository testpypi $(DIST)/*

publish: test build sign
	# upload to pypi (requires pypi account)
	twine upload --repository pypi $(DIST)/*

docker-base-test:
	# after pushing to pypi you want to check if you can pull and run
	# in a clean environment. Safest bet is to use docker!
	docker run -it python:$(PY) bash -i -c 'pip install $(PRJ); $(IMPORT_TEST); $(CLI_TEST)'

# Project Clone Target
# --------------------
# The `clone` target copies all required files to a new dir and will setup a
# new python project for you in which you can use the same build features that
# `project.mk` provides for the current project.
#
_prj_path     := $(PREFIX)/$(NEW_PRJ)
_prj_main     := $(NEW_PRJ).$(NEW_PRJ)
_prj_tests    := $(_prj_path)/tests
_prj_package  := $(PREFIX)/$(NEW_PRJ)/$(NEW_PRJ)
_prj_files    := $(patsubst %,$(_prj_path)/%,$(PRJ_FILES))
_unsafe_clone := false
_diff         := 2> /dev/null diff --color
_expr_eq      := \([ ]*=[ ]*\).*
_expr_assig   := \(-m[ ]*\|:=[ ]*\|=[ ]*\)
_expr_sub     := $(PRJ)[a-z\.]\+
_prj_test     := $(_prj_tests)/test_$(NEW_PRJ).py
_prj_test_def := def test_$(NEW_PRJ)(): pass
_clone_files  := $(PRJ_FILES) .gitignore

check-project:
	test -n "$(NEW_PRJ)" -a -n "$(PREFIX)"  # ensure that NEW_PRJ name and PREFIX path are set

check-clone: check-project
	! test -e $(_prj_path)                  # target project path must not exist

copy-tools: check-project
	mkdir -p $(_prj_path)                   # create project path
	cp -f $(PRJ_TOOLS) $(_prj_path)         # copy project tools that do not have any custom code/names

merge-project: copy-tools
	mkdir -p $(_prj_package) $(_prj_tests)  # create package path and tests path
	cp -r -n $(_clone_files) $(_prj_path)   # copy all project files (do not overwrite existing)
	sed -i 's#main$(_expr_eq)#main\1$(_prj_main)#g'        $(_prj_path)/project.cfg  # replace main module
	sed -i 's#$(_expr_assig)$(_expr_sub)#\1$(_prj_main)#g' $(_prj_files)             # replace current main in copied files
	sed -i 's#$(PRJ)#$(NEW_PRJ)#g'                         $(_prj_files)             # replace current project in copied files
	touch $(_prj_package)/__init__.py       # create python package
	touch $(_prj_package)/__main__.py       # make package runnable
	test -e $(_prj_test) || echo '$(_prj_test_def)' > $(_prj_test)  # create a test file
	$(_diff) . $(_prj_path) || true         # compare the copied files to the source files
	#-------------------------------------------
	# Cloned $(PRJ) to $(_prj_path)!            
	# If all went well you can now build it     
	#-------------------------------------------
	@echo cd $(_prj_path)                        
	@echo make                                   
	@echo make build                             
	# -------------------------------------------

clone-project: check-clone merge-project

# docker-test also runs basic import and run test
docker-test: docker-base-test
