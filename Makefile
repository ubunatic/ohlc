
PY     := 3
PYTHON := python$(PY)
PIP    := pip$(PY)

unexport PYTHONPATH

all: clean tox

clean: ; pyclean . || true
tox:   ; which tox || pip install tox; tox

test:
	# run linter + basic tests
	$(PYTHON) -m flake8 ohlc
	$(PYTHON) -m pytest -x tests

test-cli:
	tests/test-cli.sh

run: ; $(PYTHON) -m ohlc $(ARGS)

install: tox  # ensure all tests run through before installing
	$(PIP) install --user -e .

uninstall:
	$(PIP) uninstall -y ohlc || true

