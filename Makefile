# Building
# --------
# To "build" this Python project just run the tests via `make`.
# The default target will then cleanup the project dir and run the tests.
#
# Packaging
# ---------
# To package the project run `make build` and use the Python wheels in ./dist
# as packages for your needs. For pypi integration, please see `setup.mk`

PY      := 3
_PYTHON := python$(PY)
_PIP    := pip$(PY)

unexport PYTHONPATH

.PHONY: all clean tox test build install uninstall test-cli

all: clean tox

# Test and Build Targets
clean: ; rm -rf dist; pyclean .; true
tox:   ; which tox || pip install tox; tox
test:
	# running linter + basic tests using $(shell $(_PYTHON) --version)
	$(_PYTHON) -m flake8 ohlc
	$(_PYTHON) -m pytest -x tests

build: clean tox
	# building python wheel for publishing to pypi
	$(_PYTHON) setup.py bdist_wheel

# Manual Installation and Packaging Targets (for develpment only)
install: tox ; $(_PIP) install --user -e .
uninstall:   ; $(_PIP) uninstall -y ohlc || true
test-cli:    ; tests/test-cli.sh
