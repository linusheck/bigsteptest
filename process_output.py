import tabulate
import argparse
import json
import csv
from datetime import datetime

parser = argparse.ArgumentParser(description="Process output of jobs.")
parser.add_argument("files", nargs="+", help="The files to process the output of.")
parser.add_argument("--results", help="Result file.")

args = parser.parse_args()

table_headers = [
    "Model",
    "Const",
    "Mem",
    "Prop",
    "Region",
    "Region Bound",
    "Epsilon",
    "RobustPLA",
    "BigStep",
    "SplitStrat",
    "Estimate",
    "Simple",
    "#States (after)",
    "Time (wall)",
    "% Known",
    "Regions",
]
table = [table_headers]

for file in args.files:
    current_line = []

    content = None
    with open(file) as f:
        content = f.read()

    lines = content.split("\n")
    lines = [x for x in lines if not "commands.sh" in x]

    info_str = [x for x in lines if x.startswith('{"')][0]
    info_str = info_str.replace("\\", '\\"')
    info_json = json.loads(info_str)

    # Model
    if "prism" in info_json:
        current_line.append(info_json["prism"].split(".")[0])
    elif "pomdp" in info_json:
        current_line.append(info_json["pomdp"].split(".")[0])
    elif "drn" in info_json:
        current_line.append(info_json["drn"].split(".")[0])
    elif "jani" in info_json:
        current_line.append(info_json["jani"].split(".")[0])
    else:
        current_line.append("???")

    # Constants
    constants_str = ""
    for c in info_json["constants"]:
        constants_str += c + "=" + str(info_json["constants"][c]) + " "
    if constants_str == "":
        constants_str = "N/A"
    current_line.append(constants_str)

    # Memory Bound
    if "memory_bound" in info_json:
        current_line.append(str(info_json["memory_bound"]))
    else:
        current_line.append("N/A")

    # Property
    prop_dict = info_json["prop"]
    prop_str = (
        str(prop_dict["bound"])
        + "_"
        + prop_dict["type"]
        + ("_" + prop_dict["reward_model"] if "reward_model" in prop_dict else "")
        + "_"
        + prop_dict["dir"]
        + "_"
        + prop_dict["label"]
    )
    current_line.append(prop_str)
    # current_line.append("?")

    # Number of parameters
    variables_lines = [x for x in lines if x.startswith("Analyzing parameter region")]
    if len(variables_lines) == 0:
        current_line.append("?")
    else:
        current_line.append(variables_lines[-1].split(" ")[3].replace(";", ""))
    
    if "region_interval" in info_json:
        current_line.append(info_json["region_interval"])
    else:
        current_line.append(info_json["region_bound"])

    current_line.append(info_json["epsilon"])

    current_line.append(str(info_json["use_robust_pla"]).lower())
    current_line.append(str(info_json["big_step"]).lower())
    current_line.append(info_json["splitting_strategy"])
    current_line.append(info_json["estimate_method"] if "estimate_method" in info_json else "")
    current_line.append(str(info_json["simple"]).lower())

    # Number of states
    states_lines = [x for x in lines if x.startswith("States:")]
    if len(states_lines) == 0:
        current_line.append("?")
    else:
        current_line.append(states_lines[-1].split(" ")[-1])


    # Real time
    real_time = lines[-4]

    def parse_time(real_time):
        return int(real_time.split("m")[0]) * 60 + float(real_time.split("m")[1][:-1])

    # If benchmark has terminated, this will be the case:
    if lines[-7] == "Formula is satisfied by all parameter instantiations.":
        current_line.append(parse_time(real_time.split()[-1]))

        # unknown fraction
        unknown_fraction = [l for l in lines if "parameter space are not covered" in l][0]
        value = unknown_fraction.split()[0][:-1]
        current_line.append(round(100.0 - float(value), 4))

        # Total number of regions
        num_regions = [l for l in lines if "after analyzing" in l][0]
        value = num_regions.split(" ")[-2]
        current_line.append(value)
    elif lines[-7] == "Formula is not satisfied by all parameter instantiations.":
        print("Formula is not satisfied by all parameter instantiations.", file)
        current_line.append("ERR")
        current_line.append("ERR")
        current_line.append("ERR")
    else:
        if parse_time(real_time.split()[-1]) > 60*60:
            current_line.append("TO")
            current_line.append("TO")
            current_line.append("TO")
        else:
            # all other stuff is usually MO, that can come in different shapes
            current_line.append("MO")
            current_line.append("MO")
            current_line.append("MO")
    table.append(current_line)

with open(args.results, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(table)

