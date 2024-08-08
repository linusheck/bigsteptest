#!/usr/bin/env fish

mkdir -p experiments
set folder experiments/simple-$(date '+%Y-%m-%d-%H-%M-%S')
mkdir $folder

echo $folder

python3 generate_commands.py --folder testcases_simple --global-override benchmarks/simple.json --storm-location ../storm/build_release/bin/ --output $folder
./$folder/parallel.sh

set result_file $folder/results.csv
python3 process_output.py $folder/output/* --results $result_file

python3 csv_to_scatter.py $result_file false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.1" --output-pdf $folder/"time_1e-1.pdf"
python3 csv_to_scatter.py $result_file false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.01" --output-pdf $folder/"time_1e-2.pdf"
python3 csv_to_scatter.py $result_file false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.001" --output-pdf $folder/"time_1e-3.pdf"

python3 csv_to_scatter.py $result_file false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.1" --output-pdf $folder/"regions_1e-1.pdf"
python3 csv_to_scatter.py $result_file false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.01" --output-pdf $folder/"regions_1e-2.pdf"
python3 csv_to_scatter.py $result_file false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.001" --output-pdf $folder/"regions_1e-3.pdf"
