#!/usr/bin/env fish

mkdir -p experiments
set folder experiments/bigstep-$(date '+%Y-%m-%d-%H-%M-%S')
mkdir $folder

python3 generate_commands.py --folder testcases --global-override benchmarks/bigstep.json --storm-location ../storm/build_release/bin/ --output $folder --jobs 16 --timeout 3000
./$folder/parallel.sh

set result_file $folder/results.csv

python process_output.py $folder/output/* --results $result_file


function plot --description "plot <format> <separate-legend> <dpi> <title>"
    for epsilon in 0.1 0.01 0.0001 1e-05
        for region_bound in 0 0.1 1e-06 "0,0.8" "0.2,1"
            python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Time (wall)" --filter "Epsilon:$epsilon;Region Bound:$region_bound" --output-pdf $folder/"time-$(string replace . , $epsilon)-$(string replace . , $region_bound).$argv[1]" --separate-legend $argv[2] --figsize $argv[3] --title $argv[4]
            python csv_to_scatter.py $result_file true false "bigstep" "no bigstep" --compare-by "Regions" --min 0 --max 5 --filter "Epsilon:$epsilon;Region Bound:$region_bound" --output-pdf $folder/"regions-$(string replace . , $epsilon)-$(string replace . , $region_bound).$argv[1]" --separate-legend $argv[2] --figsize $argv[3] --title $argv[4]
        end
    end
end

plot pgf 1 6 0
plot pdf 0 7 1
