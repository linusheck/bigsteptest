import tabulate
import sys

if __name__ == "__main__":
    assert len(sys.argv) == 2
    with open(sys.argv[1]) as f:
        output_file = f.read()
    benchmarks = output_file.split("==new run==")
    