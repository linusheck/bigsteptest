#!/usr/bin/env fish

mkdir -p experiments
set folder experiments/bigstep-$(date '+%Y-%m-%d-%H-%M-%S')
mkdir $folder

python3 generate_commands.py --folder only --global-override benchmarks/bigstep.json --storm-location ../storm/build_release/bin/ --output $folder
./$folder/parallel.sh

set result_file $folder/results.csv

python process_output.py $folder/output/* --results $result_file

python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (MC)" --filter "Epsilon:0.1" --output-pdf $folder/"time_1e-1.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (MC)" --filter "Epsilon:0.01" --output-pdf $folder/"time_1e-2.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (MC)" --filter "Epsilon:0.001" --output-pdf $folder/"time_1e-3.pdf"

python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.1" --output-pdf $folder/"regions_1e-1.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.01" --output-pdf $folder/"regions_1e-2.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.001" --output-pdf $folder/"regions_1e-3.pdf"
