rm output/*
python3 generate_commands.py --folder testcases_simple --global-override simple.json --storm-location ../storm/build_release/bin/
./parallel.sh
python3 process_output.py output/*

python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.1"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.01"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "Time (MC)" --comp-field Simple --filter "Epsilon:0.001"

python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.1"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.01"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) false true "nonsimple" "simple" --compare-by "# Regions" --comp-field Simple --min 0 --max 5 --filter "Epsilon:0.001"
