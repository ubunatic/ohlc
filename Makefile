.PHONY: test docker-demos

MAIN := ohlc
override PY ?= 3

include project.mk

test: $(TP_FILES)
	$(PYTHON) -m $(MAIN) --help >/dev/null

docker-test:
	docker run -it python:$(PY) bash -i -c 'pip install ohlc; ohlc; true'
