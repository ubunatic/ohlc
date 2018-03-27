.PHONY: docker-test

MAIN := ohlc
TEST_SCRIPTS := \
	ohlc-input  -h; \
	ohlc-random -h; \
	test "`ohlc-input <(echo 2 1 4 3)`" == "2.000000 4.000000 1.000000 3.000000"

override PY ?= 3

include project.mk
