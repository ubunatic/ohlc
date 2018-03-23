.PHONY: test docker-demos

PRJ_MAIN := ohlc.ohlc

include project.mk

test: $(TP_FILES)
	$(PYTHON) -m $(PRJ_MAIN) --help >/dev/null

docker-test:
	docker run -it python:$(PY) bash -i -c 'pip install ohlc; ohlc all; true'
