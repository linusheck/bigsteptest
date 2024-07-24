#!/usr/bin/env fish

mkdir -p experiments
set folder experiments/simple-$(date '+%Y-%m-%d-%H-%M-%S')
mkdir $folder

echo $folder

python3 generate_commands.py --folder testcases_simple --global-override benchmarks/simple.json --storm-location ../storm/build_release/bin/ --output $folder
./$folder/parallel.sh
python3 process_output.py $folder/output/

python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.1"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.01"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.001"

python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.1"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.01"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.001"
