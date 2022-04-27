import tabulate
import argparse
import json
import csv
from datetime import datetime

parser = argparse.ArgumentParser(description="Process output of jobs.")
parser.add_argument("files", nargs="+", help="The files to process the output of.")

args = parser.parse_args()

table_headers = ["Model", "Const", "Mem", "Prop", "#States (min)", "#Params (min)", "Add. Settings", "Method", "Time", "Found"]
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
    current_line.append(str(info_json["memory_bound"]))

    # Property
    prop_dict = info_json["prop"]
    prop_str = str(prop_dict["bound"]) + "_" + prop_dict["type"] + "_" + (prop_dict["reward_model"] if "reward_model" in prop_dict else "") + "_" + prop_dict["dir"] + "_" + prop_dict["label"]
    current_line.append(prop_str)
    # current_line.append("?")

    # Number of states
    states_lines = [x for x in lines if x.startswith("States:")]
    if len(states_lines) == 0:
        current_line.append("?")
    else:
        current_line.append(states_lines[-1].split(" ")[-1])

    # Number of parameters
    variables_lines = [x for x in lines if x.startswith("Parameters:")]
    if len(variables_lines) == 0:
        current_line.append("?")
    else:
        current_line.append(len(variables_lines[-1].split(" ")) - 1)

    # Learning Rate
    current_line.append("lr="+str(info_json["learning_rate"]) + (" args="+str(info_json["additional_storm_args"]) if "additional_storm_args" in info_json else ""))
    current_line.append(str(info_json["method"]))

    # The "finished in x" line:
    finished_in_x = lines[-6]

    print(finished_in_x)

    def parse_time(real_time):
        return int(real_time.split("m")[0]) * 60 + float(real_time.split("m")[1][:-1])

    # If benchmark has not terminated, this will be the case:
    if finished_in_x.startswith("Finished in"):
        # user_time = lines[-3]
        # sys_time = lines[-2]
        # if not (user_time.startswith("user") and sys_time.startswith("sys")):
        #     print("time needs to start with correct starts")
        #     sys.exit(1)
        # current_line.append(parse_time(sys_time.split("\t")[1]) + parse_time(user_time.split("\t")[1]))
        time_as_string = finished_in_x.split(" ")[2]
        current_line.append(round(float(time_as_string[:-1]), 4))

        # The "found value at" line
        found_value_at = lines[-8]
        value = found_value_at.split(" ")[2]
        current_line.append(round(float(value), 4))
    elif finished_in_x.startswith("This procedure took"):
        # user_time = lines[-3]
        # sys_time = lines[-2]
        # if not (user_time.startswith("user") and sys_time.startswith("sys")):
        #     print("time needs to start with correct starts")
        #     sys.exit(1)
        # current_line.append(parse_time(sys_time.split("\t")[1]) + parse_time(user_time.split("\t")[1]))
        if "Qcqp" in content:
            solver_time_line = [x for x in lines if x.startswith("solver time=")][0]
            encoding_time_line = [x for x in lines if x.startswith("encoding time=")][0]
            solver_time = float(solver_time_line.split("=")[1])
            encoding_time = float(encoding_time_line.split("=")[1])
            current_line.append(round(solver_time + encoding_time, 4))
        else:
            time_as_string = finished_in_x.split(" ")[3]
            current_line.append(round(float(time_as_string[:-1]), 4))


        # The "found value at" line
        found_value_at = lines[-7]
        value = found_value_at.split(" ")[-1][:-1]
        current_line.append(round(float(value), 4))
    else:
        # TODO: we don't know how to handle GD errors, but they currently did not occur
        if info_json["method"] in ["qcqp", "pso"] and "Error" in content:
            current_line.append("ERR")
            current_line.append("ERR")
        elif info_json["method"] not in ["qcqp", "pso"] and "ERROR" in content:
            current_line.append("ERR")
            current_line.append("ERR")
        else:
            current_line.append("N/A")
            current_line.append("N/A")
    table.append(current_line)

with open('out' + str(int(datetime.now().timestamp())) + '.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(table)

print(tabulate.tabulate(table))
