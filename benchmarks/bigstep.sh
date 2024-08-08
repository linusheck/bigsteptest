#!/usr/bin/env fish

mkdir -p experiments
set folder experiments/bigstep-$(date '+%Y-%m-%d-%H-%M-%S')
mkdir $folder

python3 generate_commands.py --folder testcases --global-override benchmarks/bigstep.json --storm-location ../storm/build_release/bin/ --output $folder --jobs 32 --timeout 3000
./$folder/parallel.sh

set result_file $folder/results.csv

python process_output.py $folder/output/* --results $result_file

python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:0.1,Region Bound:0" --output-pdf $folder/"time_1e-1_0.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:0.01,Region Bound:0" --output-pdf $folder/"time_1e-2_0.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:0.0001,Region Bound:0" --output-pdf $folder/"time_1e-4_0.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:1e-05,Region Bound:0" --output-pdf $folder/"time_1e-5_0.pdf"

python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:0.1,Region Bound:0.1" --output-pdf $folder/"time_1e-1.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:0.01,Region Bound:0.1" --output-pdf $folder/"time_1e-2.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:0.0001,Region Bound:0.1" --output-pdf $folder/"time_1e-4.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:1e-05,Region Bound:0.1" --output-pdf $folder/"time_1e-5.pdf"

python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.1,Region Bound:0" --output-pdf $folder/"regions_1e-1_0.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.01,Region Bound:0" --output-pdf $folder/"regions_1e-2_0.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.0001,Region Bound:0" --output-pdf $folder/"regions_1e-4_0.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:1e-05,Region Bound:0" --output-pdf $folder/"regions_1e-5_0.pdf"

python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.1,Region Bound:0.1" --output-pdf $folder/"regions_1e-1.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.01,Region Bound:0.1" --output-pdf $folder/"regions_1e-2.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:0.0001,Region Bound:0.1" --output-pdf $folder/"regions_1e-4.pdf"
python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "# Regions" --min 0 --max 5 --filter "Epsilon:1e-05,Region Bound:0.1" --output-pdf $folder/"regions_1e-5.pdf"