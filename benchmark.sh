rm output/*
python3 generate_commands.py --folder testcases-pmcs --global-override pla_benchmark_override.json --storm-location ../storm/build_optimized/bin/
./parallel.sh
python3 process_output.py output/*

python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) true false "bigstep" "no bigstep" --compare-by "Time (MC)" --filter "Epsilon:0.1"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) true false "bigstep" "no bigstep" --compare-by "Time (MC)" --filter "Epsilon:0.05"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) true false "bigstep" "no bigstep" --compare-by "Time (MC)" --filter "Epsilon:0.01"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) true false "bigstep" "no bigstep" --compare-by "Time (MC)" --filter "Epsilon:0.005"

python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) true false "bigstep" "no bigstep" --compare-by "# Regions" --min -1 --max 5 --filter "Epsilon:0.1"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) true false "bigstep" "no bigstep" --compare-by "# Regions" --min -1 --max 5 --filter "Epsilon:0.05"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) true false "bigstep" "no bigstep" --compare-by "# Regions" --min -1 --max 5 --filter "Epsilon:0.01"
python3 csv_to_scatter.py csvs/(ls -t csvs | head -n1) true false "bigstep" "no bigstep" --compare-by "# Regions" --min -1 --max 5 --filter "Epsilon:0.005"
