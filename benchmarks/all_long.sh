#!/usr/bin/env fish

echo "Running all benchmarks"

mkdir -p experiments

set jobs 16
if test (count $argv) -gt 0
    set jobs $argv[1]
end

./benchmarks/bigstep.sh $jobs
# No bigstep-roundrobin due to time constraints
./benchmarks/bigstep_roundrobin.sh $jobs
./benchmarks/lpl_vs_standard.sh $jobs
./benchmarks/families.sh
./benchmarks/nonsimple.sh
