from pathlib import Path
from fractions import Fraction
import sys
import matplotlib.pyplot as plt

def is_parameter_discrete(param):
    # only works for our specific benchmark
    return param.startswith("P")

def get_components(interval_string):
    components = interval_string.split("<=")
    lower = components[0]
    param = components[1]
    upper = components[2]
    return lower, param, upper

def num_open(region):
    num_open = 0
    intervals = region.split(",")
    for interval in intervals:
        lower, param, upper = get_components(interval)
        if is_parameter_discrete(param) and lower != upper:
            num_open += 1
    return num_open

def region_area(region, original_region_sizes):
    intervals = region.split(",")
    area = Fraction(1)
    for interval in intervals:
        components = interval.split("<=")
        lower, param, upper = components
        if is_parameter_discrete(param):
            # We consider the area of a fixed discrete parameter to be 0.5,
            # because it represents half the area of the parameter space
            area *= Fraction(1, 2) if lower == upper else Fraction(1)
        else:
            area *= (Fraction(upper) - Fraction(lower)) / original_region_sizes[param]
    return area

if __name__ == "__main__":
    original_region = "0.4<=startsend<=0.6,0.7<=contsend<=0.9,0<=P11<=1,0<=P12<=1,0<=P21<=1,0<=P22<=1,0<=P31<=1,0<=P32<=1,0<=P41<=1,0<=P42<=1,0<=P51<=1,0<=P52<=1,0<=P61<=1,0<=P62<=1,0<=P71<=1,0<=P72<=1,0<=P81<=1,0<=P82<=1"
    # how big the original region is for each parameter
    original_region_sizes = {param: Fraction(upper) - Fraction(lower) for lower, param, upper in [get_components(x) for x in original_region.split(",")]}
    fixed_regions = 0
    known_regions = 0
    fixed_area = Fraction(0)
    fixed_areas = [Fraction(0) for i in range(19)]
    known_area = Fraction(0)

    input_file = Path(sys.argv[1])
    for line in input_file.read_text().splitlines():
        if line.startswith("All"):
            region = line.split(": ")[1]
            region = region.replace(";", "")
            area = region_area(region, original_region_sizes)
            if num_open(region) == 0:
                fixed_regions += 1
                fixed_area += area
            fixed_areas[num_open(region)] += area
            known_regions += 1
            known_area += area
    print(f"Fixed regions: {fixed_regions}/{known_regions} = {fixed_regions/known_regions}")
    print(f"Fixed area: {float(fixed_area)}/{float(known_area)} = {float(fixed_area/known_area)}")
    print(f"Open area by number of open parameters: {[float(x/known_area) for x in fixed_areas]}")

    # plot the distribution of fixed regions by number of open parameters
    plt.figure(figsize=(3, 2))  # Smaller figure size
    plt.bar(range(19), [float(x/known_area) for x in fixed_areas])
    plt.xlabel("Open Params")
    plt.ylabel("Fixed Area Fraction")
    plt.xticks(range(19))
    plt.tight_layout(pad=0.5)  # Compact layout
    plt.savefig("fixed_area_distribution.pdf", bbox_inches='tight', pad_inches=0.01)
    plt.savefig("fixed_area_distribution.pgf", bbox_inches='tight', pad_inches=0.01)
