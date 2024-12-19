#!/usr/bin/env fish

python --version

mkdir -p experiments
set folder experiments/lpl-standard-$(date '+%Y-%m-%d-%H-%M-%S')
mkdir $folder

# set jobs to --jobs <number>
set jobs 16
set timeout 3600
if test (count $argv) -gt 0
    set jobs $argv[1]
end
if test (count $argv) -gt 1
    # if command is not --short throw error
    if test $argv[2] != "--short"
        echo "Unknown argument $argv[2]"
        exit 1
    end
    set timeout 300
end


echo $folder

python3 generate_commands.py --folder testcases_standard --global-override benchmarks/lpl_vs_standard.json --storm-location ../storm/build_release/bin/ --output $folder --jobs $jobs --timeout $timeout
./$folder/parallel.sh

set result_file $folder/results.csv

python3 process_output.py $folder/output/* --results $result_file

# slowdown without enabling bigstep
python csv_to_table.py $result_file --comp-field RobustPLA --comp-values "true,false" --filter "BigStep:false" --avg-slowdown > $folder/slowdown.txt
python csv_to_table.py $result_file --comp-field RobustPLA --comp-values "false,true" --filter "BigStep:false" > $folder/table-slowdown.tex

for format in pdf pgf
    # slowdown without enabling bigstep
    python csv_to_scatter.py $result_file true false "lifted" "standard" --compare-by "Time (wall)" --comp-field "RobustPLA" --filter "BigStep:false;Epsilon:1e-05" --output-pdf $folder/"time-slowdown.$format" --separate-legend 1
    python csv_to_scatter.py $result_file true false "lifted" "standard" --compare-by "Regions" --comp-field "RobustPLA" --filter "BigStep:false;Epsilon:1e-05" --output-pdf $folder/"regions-slowdown.$format" --separate-legend 1

    # robustpl+bigstep vs standard
    python csv_to_scatter.py $result_file true false "lifted+bigstep" "standard" --compare-by "Time (wall)" --comp-field "RobustPLA" --ignore "BigStep" --filter "BigStep:%RobustPLA;Epsilon:1e-05" --output-pdf $folder/"time-st-big.$format" --separate-legend 1
    python csv_to_scatter.py $result_file true false "lifted+bigstep" "standard" --compare-by "Regions" --comp-field "RobustPLA" --ignore "BigStep" --filter "BigStep:%RobustPLA;Epsilon:1e-05"  --min 0 --max 5 --output-pdf $folder/"regions-st-big.$format" --separate-legend 1
end
