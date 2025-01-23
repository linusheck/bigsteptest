#!/usr/bin/env fish

set datetime (date "+%Y-%m-%d-%H-%M-%S")

cd casestudies/nonsimple
./benchmark.sh > ../../experiments/nonsimple-$datetime.log 2>&1
python make_table.py ../../experiments/nonsimple-$datetime.log > ../../experiments/nonsimple-$datetime-table.tex
