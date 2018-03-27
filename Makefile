.PHONY: docker-test

MAIN := ohlc
override PY ?= 3

include project.mk

docker-test:
	docker run -it python:$(PY) bash -i -c 'pip install ohlc; ohlc -h; true'
