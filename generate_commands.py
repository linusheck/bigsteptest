import glob
import subprocess
import argparse
from datetime import datetime
from os import path, makedirs, system, getcwd, chmod
import json
import sys

parser = argparse.ArgumentParser(description='Generate testcases.')
parser.add_argument('--storm-pars', type=str, default="~/storm/build/bin/storm-pars",
                    help='location of the storm-pars binary')
parser.add_argument('--times', type=int, default=1,
                    help='run stuff n times')
parser.add_argument('--exact', type=bool, default=False,
                    help='run stuff exactly')
parser.add_argument('--storm-pomdp', type=str, default="~/storm/build/bin/storm-pomdp",
                    help="location of storm-pomdp binary")
parser.add_argument('--pipenv-dir', type=str, default="~/stormlinus/",
                    help="location of pipenv directory")
parser.add_argument('--prophesy-dir', type=str, default="~/stormlinus/prophesy/",
                    help="location of prophesy directory")
parser.add_argument('--only-feasible', type=bool, default=True,
                    help="only include feasible instantiation problems")
parser.add_argument('--dry-run', type=bool, default=False,
                    help="dry run")
parser.add_argument('--folder', type=str, default="testcases",
                    help="testcases folder")
parser.add_argument('--global-override', type=str, default=None,
                    help="global override json file - change stuff in every testcase")
parser.add_argument('--print-states', type=bool, default=False,
                    help="just print states from storm-podmp")
args = parser.parse_args()

current_time = datetime.now().strftime("%Y-%b-%d-%H-%M-%S")

slurm_script = ""
manual_script = ""
number_of_task = 0


global_override_struct = {}
if args.global_override:
    with(open(args.global_override)) as global_override_file:
        global_override_struct = json.loads(global_override_file.read())

for config_file in glob.glob(args.folder + "/**/config.json"):
    folder = "/".join(config_file.split("/")[:-1])
    config = None
    with open(config_file) as f:
        config = f.read()
    config = json.loads(config)


    # Preprocess json config by unwrapping all arrays in x into multiple objects of x
    unwrapped_config = []
    for invocation in config:
        for key in global_override_struct:
            invocation[key] = global_override_struct[key]
        list_children = []
        for child in invocation.keys():
            if isinstance(invocation[child], list):
                list_children.append(child)
        if len(list_children) == 0:
            unwrapped_config.append(invocation)
        else:
            invocations = [invocation]
            for child_to_unwrap in list_children:
                new_invocations = []
                for old_invocation in invocations:
                    for x in old_invocation[child_to_unwrap]:
                        new_invocation = old_invocation.copy()
                        new_invocation[child_to_unwrap] = x
                        new_invocations.append(new_invocation)
                invocations = new_invocations
            for i in invocations:
                unwrapped_config.append(i)

    config = unwrapped_config


    for invocation in config:
        # Run storm-pomdp on the prism file to make a pmc
        constant_strings = []
        for key in invocation["constants"]:
            constant_strings.append(key + "=" + str(invocation["constants"][key]))
        constant_string = ",".join(constant_strings)

        # The prop given to storm_pomdp and to gradient descent.
        prop = ""
        prop_dict = invocation["prop"]
        if prop_dict["type"] == "reward":
            prop += "R"
        elif prop_dict["type"] == "probability":
            prop += "P"
        else:
            print("Invalid prop in", invocation)
            sys.exit(1)

        prophesy_prop = prop
        if "reward_model" in prop_dict:
            prop += "{\"" + prop_dict["reward_model"] + "\"}"
        
        prop += prop_dict["dir"]
        
        prophesy_prop += "=?"
        if prop_dict["bound"] == None:
            if args.only_feasible:
                print("Skipping non-feasible invocation.")
                continue
            prop += "=?"
        else:
            if prop_dict["dir"] == "max":
                prop += ">=" + str(prop_dict["bound"])
            if prop_dict["dir"] == "min":
                prop += "<=" + str(prop_dict["bound"])
        
        x = ""
        if prop_dict["label"].startswith("\""):
            x = " [{}]".format(prop_dict["label"])
        else:
            x = " [F \"{}\"]".format(prop_dict["label"])
        prop += x
        prophesy_prop += x

        escaped_prop = prop.replace("\"", "\\\"")

        drn_file = None
        states_table = None
        if "prism" in invocation:
            drn_file = getcwd() + "/.build/" + folder + "/" + "_".join([invocation["prism"].split(".")[0], prop_dict["type"], prop_dict["dir"], str(prop_dict["bound"]), prop_dict["label"].replace(" ", "_").replace("\"", ""), prop_dict["reward_model"] if "reward_model" in prop_dict else "", constant_string, str(invocation["memory_bound"])]) + ".drn"
            storm_pomdp_command = "{binary} --parametric-drn {drn_file} --prism {prism} -prop \"{prop}\" -const '{constant_string}' " + \
                "--buildfull --selfloopreduction --transformsimple --exact --io:no-drn-placeholders --memorybound {memory_bound}"
            storm_pomdp_command = storm_pomdp_command.format(
                binary = args.storm_pomdp,
                drn_file = drn_file,
                constant_string = constant_string,
                prop = escaped_prop,
                prism = folder + "/" + invocation["prism"],
                memory_bound = invocation["memory_bound"],
            )
            makedirs("/".join(drn_file.split("/")[:-1]), exist_ok=True)
            if path.exists(drn_file):
                print("Skipping...")
            elif args.dry_run:
                print(storm_pomdp_command)
            else:
                output = subprocess.getoutput(storm_pomdp_command)

            storm_pomdp_command_simple = "{binary} --prism {prism} -const '{constant_string}' --memorybound {memory_bound} -prop \"{prop}\"".format(
                binary = args.storm_pomdp,
                constant_string = constant_string,
                prism = folder + "/" + invocation["prism"],
                memory_bound = invocation["memory_bound"],
                prop = escaped_prop,
            )
            print(storm_pomdp_command_simple)
            output = subprocess.getoutput(storm_pomdp_command_simple)
            print(output)
            lines = output.split("\n")
            def filter_to_line(prefix):
                return int([x for x in lines if x.startswith(prefix)][0].split(" ")[1])
            states = filter_to_line("States:")
            transitions = filter_to_line("Transitions:")
            choices = filter_to_line("Choices:")
            observations = filter_to_line("Observations:")
            states_table = {
                "states": states,
                "transitions": transitions,
                "choices": choices,
                "observations": observations
            }
            print(states_table)
        elif "drn" in invocation:
            drn_file = getcwd() + "/" + folder + "/" + invocation["drn"]
        else:
            print(invocation)
            print("Neither a prism nor a drn file specified!")
            sys.exit(1)

        if args.print_states:
            continue
        invocation["states_table"] = states_table

        # Run everything n times
        for i in range(args.times):
            method = invocation["method"]
            command = "time {binary} --explicit-drn {file} --prop \"{property}\" {method} -bisim --regionbound 0.1 --refine 0.1 {exact} {additional_storm_args}".format(
                binary = args.storm_pars,
                file = drn_file,
                property = escaped_prop,
                method = "--time-travel" if method == "tt" else "",
                exact = "--exact" if args.exact else "",
                additional_storm_args = invocation["additional_storm_args"] if "additional_storm_args" in invocation else ""
            )

            json_str = json.dumps(invocation)
            slurm_script += "if [[ \"$SLURM_ARRAY_TASK_ID\" -eq " + "" + str(number_of_task) + " ]]\n"
            slurm_script += "then\n"
            slurm_script += "echo \"" + json_str.replace("\"", "\\\"") + "\"\n"
            slurm_script += command + "\n"
            slurm_script += "fi \n\n"

            manual_script += command + " | tee " + json_str.replace("\"", "").replace("{", "").replace("}", "").replace(".", "").replace(" ", "").replace(",", "-") + ".out" + "\n"

            number_of_task += 1

if args.dry_run:
    print(slurm_script)
    sys.exit(0)

slurm_command_file_name = "slurm_commands" + str(int(datetime.now().timestamp())) + ".sh"
manual_command_file_name = "manual_commands" + str(int(datetime.now().timestamp())) + ".sh"

with open(slurm_command_file_name, "w") as command_file:
    command_file.write(slurm_script)
with open(manual_command_file_name, "w") as command_file:
    command_file.write(manual_script)

chmod(slurm_command_file_name, 0o777)
chmod(manual_command_file_name, 0o777)

hpc_template_file = open("hpc.template.sh")
content = hpc_template_file.read()
hpc_template_file.close()

content = content.format(
    num=str(number_of_task - 1),
    command_file=slurm_command_file_name
)

with open("hpc.sh", "w") as hpc_out_file:
        hpc_out_file.write(content)
