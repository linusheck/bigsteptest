import tabulate
import sys

# this is a very ad-hoc table generator, and it only works for this casestudy
# Q1 and Q2 use a much more flexible system
# here, we checked everything manually in the log-file

if __name__ == "__main__":
    assert len(sys.argv) == 2
    with open(sys.argv[1]) as f:
        output_file = f.read()
    benchmarks = output_file.split("==new run==")[1:]
    benchmark_lines = [b.split("\n") for b in benchmarks]
    executed_in_lines = [[l for l in b if "Executed in" in l] for b in benchmark_lines]
    times = [l[0].split()[2] for l in executed_in_lines]
    factor_names = [l[0].split()[3] for l in executed_in_lines]
    factors = []
    for f in factor_names:
        if f == "millis":
            factors.append(1e-3)
        elif f == "secs":
            factors.append(1)
        else:
            raise ValueError(f"Unknown factor {f}")
    runtimes = [round(float(t) * f, 2) for t, f in zip(times, factors)]
    # remove runtimes where there was no result (its always a mem-out, as we have no timeout)
    runtimes = [r if any("Time for model checking" in l for l in benchmark_lines[i]) else "MO" for i, r in enumerate(runtimes)]
    # hardcoded for simplicity! if you change the experiment, change this script
    header = ["$n$", "MDP, $R_1$", "iMC, $R_1$", "iMC, $R_2$", "iMC, $R_3$"]
    table = [header]
    n_values = list(range(2, 33))
    for row, n_value in enumerate(n_values):
        row_values = [n_value]
        for i in range(row * 4, (row + 1) * 4):
            row_values.append(runtimes[i])
        table.append(row_values)
    tabulate.LATEX_BOOKTABS_ESCAPE_RULES = {}
    print(tabulate.tabulate(table, tablefmt="latex_booktabs").replace("\\$", "$").replace("lllll", "rrrrr").replace("\\_", "_"))
    