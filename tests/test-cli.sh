#!/usr/bin/env bash
set -o errexit
set -o xtrace

ohlc -h
ohlc-input  -h
ohlc-random -h
test "`ohlc-input <(echo 2 1 4 3)`" == "2.000000 4.000000 1.000000 3.000000"
