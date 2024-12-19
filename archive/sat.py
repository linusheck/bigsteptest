filenames = open("archive/sat.txt").read()
import os
from fractions import Fraction

for filename in filenames.splitlines():
    contents = open(filename).read()
    lines = contents.splitlines()
    extremal_value_line = [line for line in lines if line.startswith("Extremal value: ")][0]
    extremal_value = extremal_value_line.split(": ")[1]
    filename = filename.split("/")[-1].replace(".out", "")
    done = False
    for appendix in ["_", "_1"]:
        filename = "_".join(filename.split("_")[:-1]) + appendix
        model = filename.split("_")[0]
        if model.startswith("herman"):
            model = "herman"
        if model.startswith("newgrid") or model.startswith("4x4"):
            model = "grids"
        gdresult = f"build/testcases_standard/{model}/{filename}.gdresult"
        if not os.path.exists(gdresult):
            continue
        extremal_value = float(Fraction(extremal_value))
        print(f"Write {extremal_value} to {gdresult}")
        open(gdresult, "w").write(str(extremal_value))
        done = True
    assert done, filename