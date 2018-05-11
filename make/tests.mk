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

.PHONY: test lint base-test script-test dist-test docker-test

# The main module of the project is usually the same as the main package of the project.
# Make sure the setup the __init__.py correctly. We can then use the module to setup
# generic import and cli tests. Override the following vars as needed.
CLI_TEST     = $(PYTHON) -m $(MAIN) -h $(NOL)
IMPORT_TEST  = $(PYTHON) -c "import $(MAIN) as m; print(\"version:\",m.__version__,\"tag:\",m.__tag__)"
DIST_TEST    = $(IMPORT_TEST); $(CLI_TEST)
BASH         = bash -it -o errexit -c

# The `test` target depends on `base-test` to trigger import tests, cli tests, and linting.
# To setup yor own linting and tests, please override the `test` and `lint` targets.
test: lint base-test
lint: vars ; $(MAKEPY) lint

# Generic tests included when running `make test`.
base-test: $(SRC_FILES) pyclean vars lint
	$(IMPORT_TEST)
	$(MAKEPY) test --tests $(PRJ_TESTS)
	$(CLI_TEST)

# Test the installed package scripts (CLI tools of the package)
SCRIPT_TEST = echo "please set SCRIPT_TEST = <shell-script-code> to run script tests"
script-test:
	$(BASH) '$(SCRIPT_TEST)' $(NOL)

# run tests using default pip and python outside of the project
dist-test:
	cd tests && python -m pytest -x .
	cd /tmp && $(BASH) '$(DIST_TEST)' $(NOL)

# After pushing to PyPi, you want to check if you can pull and run
# your package in a clean environment. Safest bet is to use docker!
TEST_IMG     = python:$(PY)
TEST_VOLUMES = -v $(CURDIR)/tests:/tests
docker-test:
	docker run -it $(TEST_VOLUMES) $(TEST_IMG) 'set -o errexit; pip install $(PKG); $(DIST_TEST)'
