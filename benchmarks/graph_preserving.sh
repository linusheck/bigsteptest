#!/usr/bin/env fish

mkdir -p experiments
set folder experiments/graph-preserving-$(date '+%Y-%m-%d-%H-%M-%S')
mkdir $folder

echo $folder

python3 generate_commands.py --folder testcases --drop-region-bound True --global-override benchmarks/graph_preserving.json --storm-location ../storm/build_release/bin/ --output $folder --jobs 16 --timeout 600
./$folder/parallel.sh

set result_file $folder/results.csv

python3 process_output.py $folder/output/* --results $result_file

python3 csv_to_scatter.py $result_file 1e-06 0 "bound=1e-6" "bound=0" --compare-by "Time (MC)" --comp-field "Region Bound" --output-pdf $folder/"time_robust_plain.pdf"
python3 csv_to_scatter.py $result_file 1e-06 0 "bound=1e-6" "bound=0" --compare-by "# Regions" --min 0 --max 6 --comp-field "Region Bound" --output-pdf $folder/"regions_robust_plain.pdf"
