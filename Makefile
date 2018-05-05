MAIN := ohlc
PY   := 3
TEST_SCRIPTS := \
	ohlc -h; \
	ohlc-input  -h; \
	ohlc-random -h; \
	test "`ohlc-input <(echo 2 1 4 3)`" == "2.000000 4.000000 1.000000 3.000000"

include make/vars.mk
include make/project.mk
include make/tests.mk
include make/twine.mk
