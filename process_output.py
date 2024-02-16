import tabulate
import argparse
import json
import csv
from datetime import datetime

parser = argparse.ArgumentParser(description="Process output of jobs.")
parser.add_argument("files", nargs="+", help="The files to process the output of.")

args = parser.parse_args()

table_headers = ["Model", "Const", "Mem", "Prop", "Param Region", "BigStep Horizon", "Time-Travelling", "#States (after)",  "Time", "% Known", "# Regions"]
table = [table_headers]

for file in args.files:
    current_line = []

    content = None
    with open(file) as f:
        content = f.read()

    lines = content.split("\n")
    lines = [x for x in lines if not "commands.sh" in x]

    info_str = [x for x in lines if x.startswith("{\"")][0]
    info_str = info_str.replace("\\", "\\\"")
    info_json = json.loads(info_str)

    # Model
    if "prism" in info_json:
        current_line.append(info_json["prism"].split(".")[0])
    if "pomdp" in info_json:
        current_line.append(info_json["pomdp"].split(".")[0])
    elif "drn" in info_json:
        current_line.append(info_json["drn"].split(".")[0])
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
    prop_str = str(prop_dict["bound"]) + "_" + prop_dict["type"] + ("_" + prop_dict["reward_model"] if "reward_model" in prop_dict else "") + "_" + prop_dict["dir"] + "_" + prop_dict["label"]
    current_line.append(prop_str)
    # current_line.append("?")

    # Number of parameters
    variables_lines = [x for x in lines if x.startswith("Analyzing parameter region")]
    if len(variables_lines) == 0:
        current_line.append("?")
    else:
        current_line.append(variables_lines[-1].split(" ")[3].replace(";", ""))

    current_line.append(info_json["horizon"])
    current_line.append(info_json["timetravel"])

    # Number of states
    states_lines = [x for x in lines if x.startswith("States:")]
    if len(states_lines) == 0:
        current_line.append("?")
    else:
        current_line.append(states_lines[-1].split(" ")[-1])


    # The "finished in x" line:
    finished_in_x = lines[-4]

    def parse_time(real_time):
        return int(real_time.split("m")[0]) * 60 + float(real_time.split("m")[1][:-1])

    # If benchmark has not terminated, this will be the case:
    if finished_in_x.startswith("Time for model checking"):
        # user_time = lines[-3]
        # sys_time = lines[-2]
        # if not (user_time.startswith("user") and sys_time.startswith("sys")):
        #     print("time needs to start with correct starts")
        #     sys.exit(1)
        # current_line.append(parse_time(sys_time.split("\t")[1]) + parse_time(user_time.split("\t")[1]))
        time_as_string = finished_in_x.split(" ")[4]
        current_line.append(round(float(time_as_string[:-2]), 4))

        # unknown fraction
        unknown_fraction = [l for l in lines if "Unknown fraction" in l][0]
        value = unknown_fraction.split(" ")[-1][:-1]
        current_line.append(round(100.0 - float(value), 4))

        # unknown fraction
        unknown_fraction = [l for l in lines if "Total number of regions" in l][0]
        value = unknown_fraction.split(" ")[-1][:-1]
        current_line.append(value)
    else:
        if "Received signal 14" in content:
            current_line.append("TO")
            current_line.append("TO")
        else:
            current_line.append("ERR")
            current_line.append("ERR")
    table.append(current_line)

with open('csvs/out' + str(int(datetime.now().timestamp())) + '.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(table)

print(tabulate.tabulate(table))
