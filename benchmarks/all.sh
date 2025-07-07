#!/usr/bin/env fish

echo "Running all benchmarks"

mkdir -p experiments

set jobs 16
if test (count $argv) -gt 0
    set jobs $argv[1]
end

./benchmarks/bigstep.sh $jobs --short
./benchmarks/bigstep_roundrobin.sh $jobs --short
./benchmarks/lpl_vs_standard.sh $jobs --short
./benchmarks/families.sh
./benchmarks/nonsimple.sh
