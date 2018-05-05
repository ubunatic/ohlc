# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for
# easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/vars.mk` and `include make/tests.mk` in your `Makefile`.
# Now you can use `make`, `make test`, `make lint`, etc.
# See each target for more details.

.PHONY: test lint base-test script-test dist-test docker-test

# The main module of the project is usually the same as the main package of the project.
# Make sure the setup the __init__.py correctly. We can then use the module to setup
# generic import and cli tests. Override the following vars as needed.
TEST_SCRIPTS =
CLI_TEST     = $(PYTHON) -m $(MAIN) -h $(NOL)
IMPORT_TEST  = $(PYTHON) -c "import $(MAIN) as m; print(\"version:\",m.__version__,\"tag:\",m.__tag__)"
DIST_TEST    = $(IMPORT_TEST); $(CLI_TEST); $(TEST_SCRIPTS)
DOCKER_CLI_TEST = pip install $(PKG); $(DIST_TEST)
BASH_INIT    = set -o errexit; export TERM=xterm;
MAKEPY       = $(PYTHON) -m makepy

# The `test` target depends on `base-test` to trigger import tests, cli tests, and linting.
# To setup yor own linting and tests, please override the `test` and `lint` targets.
test: lint base-test
lint: vars ; $(MAKEPY) lint

# Generic tests included when running `make test`.
base-test: $(SRC_FILES) pyclean vars lint
	# IMPORT_TEST
	$(IMPORT_TEST)
	# MAKEPY test
	$(MAKEPY) test --tests $(PRJ_TESTS)
	# CLI_TEST
	$(CLI_TEST)

# Test the installed package scripts (CLI tools of the package)
script-test:
	bash -it -c '$(BASH_INIT) $(TEST_SCRIPTS)' $(NOL)

# use default pip and python to safely install the project in the system
dist-test:
	cd tests && python -m pytest -x .
	cd /tmp && bash -it -c '$(BASH_INIT) $(DIST_TEST)' $(NOL)

docker-test:
	# After pushing to PyPi, you want to check if you can pull and run
	# your package in a clean environment. Safest bet is to use docker!
	docker run -it python:$(PY) bash -it -c '$(BASH_INIT) $(DOCKER_CLI_TEST)'

