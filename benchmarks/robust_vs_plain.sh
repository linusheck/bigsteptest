#!/usr/bin/env fish

mkdir -p experiments
set folder experiments/robust-$(date '+%Y-%m-%d-%H-%M-%S')
mkdir $folder

echo $folder

python3 generate_commands.py --folder testcases --global-override benchmarks/robust_vs_plain.json --storm-location ../storm/build_release/bin/ --output $folder --jobs 32 --timeout 600
./$folder/parallel.sh

set result_file $folder/results.csv

python3 process_output.py $folder/output/* --results $result_file

python3 csv_to_scatter.py $result_file true false "Robust PLA" "Standard PLA" --compare-by "Time (MC)" --comp-field RobustPLA --filter "Estimate:delta" --output-pdf $folder/"time_robust_plain.pdf"
python3 csv_to_scatter.py $result_file true false "Robust PLA" "Standard PLA" --compare-by "# Regions" --min 0 --max 6 --comp-field RobustPLA --filter "Estimate:delta" --output-pdf $folder/"regions_robust_plain.pdf"

python3 csv_to_scatter.py $result_file "estimate" "roundrobin" "State-value-delta estimate" "Round-robin" --compare-by "Time (MC)" --comp-field SplitStrat --filter "Estimate:delta"
python3 csv_to_scatter.py $result_file "estimate" "roundrobin" "State-value-delta estimate" "Round-robin" --compare-by "# Regions" --min 0 --max 6 --comp-field SplitStrat --filter "Estimate:delta"

python3 csv_to_scatter.py $result_file "delta" "minmaxdelta" "State-value-delta estimate (classic)" "Min-max delta (robust)" --compare-by "Time (MC)" --comp-field Estimate --filter "SplitStrat:estimate" --ignore RobustPLA,BigStep
python3 csv_to_scatter.py $result_file "delta" "minmaxdelta" "State-value-delta estimate (classic)" "Min-max delta (robust)" --compare-by "# Regions" --min 0 --max 6 --comp-field Estimate --filter "SplitStrat:estimate" --ignore RobustPLA,BigStep

python3 csv_to_scatter.py $result_file "delta" "deltaweighted" "Delta" "Delta (Weighted)" --compare-by "Time (MC)" --comp-field Estimate --filter "SplitStrat:estimate" --ignore RobustPLA,BigStep
python3 csv_to_scatter.py $result_file "delta" "deltaweighted" "Delta" "Delta (Weighted)" --compare-by "# Regions" --min 0 --max 6 --comp-field Estimate --filter "SplitStrat:estimate" --ignore RobustPLA,BigStep
