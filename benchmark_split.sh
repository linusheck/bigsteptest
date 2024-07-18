rm output/*
python3 generate_commands.py --folder testcases --global-override robust_vs_plain.json --storm-location ../storm/build_release/bin/
./parallel.sh
python3 process_output.py output/*

python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) "estimate" "roundrobin" "State-value-delta estimate" "Round-robin" --compare-by "Time (MC)" --comp-field SplitStrat --filter "Estimate:delta"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) "estimate" "roundrobin" "State-value-delta estimate" "Round-robin" --compare-by "# Regions" --min 0 --max 6 --comp-field SplitStrat --filter "Estimate:delta"

python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) "delta" "minmaxdelta" "State-value-delta estimate (classic)" "Min-max delta (robust)" --compare-by "Time (MC)" --comp-field Estimate --filter "SplitStrat:estimate" --ignore RobustPLA,BigStep
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) "delta" "minmaxdelta" "State-value-delta estimate (classic)" "Min-max delta (robust)" --compare-by "# Regions" --min 0 --max 6 --comp-field Estimate --filter "SplitStrat:estimate" --ignore RobustPLA,BigStep



python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) "delta" "deltaweighted" "Delta" "Delta (Weighted)" --compare-by "Time (MC)" --comp-field Estimate --filter "SplitStrat:estimate" --ignore RobustPLA,BigStep
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) "delta" "deltaweighted" "Delta" "Delta (Weighted)" --compare-by "# Regions" --min 0 --max 6 --comp-field Estimate --filter "SplitStrat:estimate" --ignore RobustPLA,BigStep
