#!/usr/bin/env fish

set datetime (date "+%Y-%m-%d-%H-%M-%S")

cd casestudies/dpm
./benchmark.sh > ../../experiments/q4-families-$datetime.log 2>&1
