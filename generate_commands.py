import glob
import subprocess
import argparse
from datetime import datetime
from os import path, makedirs, system, getcwd, chmod
import json
import sys
from pathlib import Path


# Preprocess json config by unwrapping all arrays in x into multiple objects of x
def unwrap_config(config: dict, global_override: dict) -> dict:
    unwrapped_config = []
    if not isinstance(global_override, list):
        global_override = [global_override]
    for override in global_override:
        for invocation in config:
            for key in override:
                invocation[key] = override[key]
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
    return unwrapped_config


def create_prop_from_dict(prop_dict: dict, gd_prop=False) -> str:
    prop = ""
    if prop_dict["type"] == "reward":
        prop += "R"
    elif prop_dict["type"] == "probability":
        prop += "P"
    else:
        return None

    if "reward_model" in prop_dict:
        prop += '{"' + prop_dict["reward_model"] + '"}'

    prop += prop_dict["dir"]

    if prop_dict["bound"] is None:
        prop += "=?"
    else:
        if prop_dict["dir"] == "max":
            prop += ("<=" + str(-1) if gd_prop else ">=" + str(prop_dict["bound"]))
        if prop_dict["dir"] == "min":
            prop += (">=" + str(1e9) if gd_prop else "<=" + str(prop_dict["bound"]))

    label = prop_dict["label"]
    if label.startswith('"'):
        prop += f" [{label}]"
    else:
        prop += f' [F "{label}"]'
    return prop.replace('"', '\\"')


def bool_to_cli_string(b):
    if b:
        return "true"
    else:
        return "false"


def create_file_name(invocation: dict, constant_string: str) -> str:
    prop_dict = invocation["prop"]
    return (
        "_".join(
            [
                invocation["pomdp"].split(".")[0] if "pomdp" in invocation else invocation["prism"].split(".")[0],
                prop_dict["type"],
                prop_dict["dir"],
                prop_dict["label"].replace(" ", "_").replace('"', ""),
                prop_dict["reward_model"] if "reward_model" in prop_dict else "",
                constant_string,
                str(invocation["memory_bound"]) if "memory_bound" in invocation else "",
            ]
        )
    )


def main():
    parser = argparse.ArgumentParser(description="generate testcases.")
    parser.add_argument(
        "--storm-location",
        type=Path,
        default="~/git/storm/build/bin/",
        help="location of the storm binaries (in particular, storm-pars and storm-pomdp)",
    )
    parser.add_argument("--times", type=int, default=1, help="run stuff n times")
    parser.add_argument("--dry-run", type=bool, default=False, help="dry run")
    parser.add_argument(
        "--folder", type=Path, default="testcases", help="testcases folder"
    )
    parser.add_argument(
        "--global-override",
        type=Path,
        default=None,
        help="global override json file - change stuff in every testcase",
    )
    args = parser.parse_args()

    slurm_script = ""
    manual_script = ""
    number_of_task = 0

    global_override = {}
    if args.global_override:
        global_override = json.loads(args.global_override.read_text())

    for config_file_name in glob.glob(str(args.folder) + "/**/config.json"):
        config_file = Path(config_file_name)
        folder = config_file.parent
        config = unwrap_config(
            json.loads(config_file.read_text(encoding="utf-8")), global_override
        )

        for invocation in config:
            # run storm-pomdp on the prism file to make a pmc
            constant_strings = []
            for key in invocation["constants"]:
                constant_strings.append(key + "=" + str(invocation["constants"][key]))
            constant_string = ",".join(constant_strings)

            prop = create_prop_from_dict(invocation["prop"])
            gd_prop = create_prop_from_dict(invocation["prop"], gd_prop=True)

            drn_file = None
            prism_file = None

            if "pomdp" in invocation:
                drn_file = (
                    Path(getcwd())
                    / ".build"
                    / folder
                    / (create_file_name(invocation, constant_string) + ".drn")
                )
                storm_pomdp_command = (
                    "{binary} --parametric-drn {drn_file} --prism {pomdp} -prop \"{prop}\" -const '{constant_string}' "
                    + "--buildfull --transformsimple --selfloopreduction --exact --io:no-drn-placeholders --memorybound {memory_bound}"
                )
                storm_pomdp_command = storm_pomdp_command.format(
                    binary=args.storm_location / "storm-pomdp",
                    drn_file=drn_file,
                    constant_string=constant_string,
                    prop=prop,
                    pomdp=folder / invocation["pomdp"],
                    memory_bound=invocation["memory_bound"],
                )
                makedirs(drn_file.parent, exist_ok=True)
                if path.exists(drn_file):
                    pass
                elif args.dry_run:
                    print(storm_pomdp_command)
                else:
                    output = subprocess.getoutput(storm_pomdp_command)
                    print(output)
                print(drn_file)
            elif "prism" in invocation:
                prism_file = getcwd() / folder / invocation["prism"]
                print(prism_file)
            elif "drn" in invocation:
                drn_file = getcwd() + "/" + folder + "/" + invocation["drn"]
            else:
                print(invocation)
                print("neither a prism nor a drn file specified!")
                sys.exit(1)

            gd_result_file = (
                Path(getcwd())
                / ".build"
                / folder
                / (create_file_name(invocation, constant_string) + ".gdresult")
            )

            if gd_result_file.exists():
                found_bound = float(gd_result_file.read_text())
            else:
                # find a good bound with GD
                timeout = 4
                while True:
                    gd_command = '{binary} {file} {constants} -prop "{property}" --mode feasibility --feasibility:method gd --regionbound 0.01 -bisim --timeout {timeout}'.format(
                        binary=(
                            Path(invocation["storm_location"]) / "storm-pars"
                            if "storm_location" in invocation
                            else args.storm_location / "storm-pars"
                        ),
                        file=(
                            "--explicit-drn " + str(drn_file)
                            if drn_file
                            else "--prism " + str(prism_file)
                        ),
                        constants=(
                            ""
                            if (drn_file or not constant_string)
                            else "-const " + constant_string
                        ),
                        property=gd_prop,
                        timeout=timeout
                    )
                    print(gd_command)
                    output_gd = subprocess.getoutput(gd_command)
                    values = [float(l.split(" ")[-1]) for l in output_gd.split("\n") if "Best found value so far" in l]
                    if len(values) > 0:
                        found_bound = values[-1]
                        print(f"Found GD bound {found_bound}")
                        makedirs(gd_result_file.parent, exist_ok=True)
                        gd_result_file.write_text(str(found_bound))
                        break
                    timeout = 2 * timeout
                    print(f"Increasing timeout to {timeout}")

            invocation["prop"]["bound"] = found_bound * ((1 + invocation["epsilon"]) if invocation["prop"]["dir"] == "min" else (1 - invocation["epsilon"]))
            prop = create_prop_from_dict(invocation["prop"])
            print(prop)

            # run everything n times
            for i in range(args.times):
                use_robust_pla = (
                    "use_robust_pla" in invocation and invocation["use_robust_pla"]
                )
                command = '{binary} {file} {constants} -prop "{property}" {method} --mode partitioning --regionbound 0.01 --terminationCondition 0 {robust_pla} -bisim {additional_storm_args} --splitting-strategy roundrobin --splitting-threshold 2'.format(
                    binary=(
                        Path(invocation["storm_location"]) / "storm-pars"
                        if "storm_location" in invocation
                        else args.storm_location / "storm-pars"
                    ),
                    file=(
                        "--explicit-drn " + str(drn_file)
                        if drn_file
                        else "--prism " + str(prism_file)
                    ),
                    constants=(
                        ""
                        if (drn_file or not constant_string)
                        else "-const " + constant_string
                    ),
                    property=prop,
                    method=(
                        "--big-step"
                        if "big_step" in invocation and invocation["big_step"]
                        else ""
                    ),
                    robust_pla=(
                        "--regionverif:engine robustpl --minmax:method vi"
                        if use_robust_pla
                        else "--minmax:method vi"  # TODO assuming VI
                    ),
                    additional_storm_args=(
                        invocation["additional_storm_args"]
                        if "additional_storm_args" in invocation
                        else ""
                    ),
                )

                json_str = json.dumps(invocation)
                echo_str = json_str.replace('\\"', "").replace('"', '\\"')

                slurm_script += (
                    'if [[ "$SLURM_ARRAY_TASK_ID" -eq '
                    + ""
                    + str(number_of_task)
                    + " ]]\n"
                )
                slurm_script += "then\n"
                slurm_script += 'echo "' + echo_str + '"\n'
                slurm_script += "time " + command + "\n"
                slurm_script += "fi \n\n"

                manual_script += (
                    '( echo "'
                    + echo_str
                    + '"'
                    + " && time timeout 600 "
                    + command
                    + "  ) > "
                    + "output/"
                    + json_str.replace('"', "")
                    .replace("{", "")
                    .replace("}", "")
                    .replace(".", "")
                    .replace(" ", "")
                    .replace(",", "-")
                    .replace(">", "greater")
                    .replace("<", "less")
                    .replace("~", "home")
                    .replace("/", "slash")
                    + ".out 2>&1"
                    + "\n"
                )

                number_of_task += 1

    if args.dry_run:
        print(slurm_script)
        sys.exit(0)

    makedirs("scripts", exist_ok=True)
    makedirs("output", exist_ok=True)

    slurm_command_file_name = (
        "scripts/slurm_commands" + str(int(datetime.now().timestamp())) + ".sh"
    )
    manual_command_file_name = (
        "scripts/manual_commands" + str(int(datetime.now().timestamp())) + ".sh"
    )

    with open(slurm_command_file_name, "w") as command_file:
        command_file.write(slurm_script)
    with open(manual_command_file_name, "w") as command_file:
        command_file.write(manual_script)

    chmod(slurm_command_file_name, 0o777)
    chmod(manual_command_file_name, 0o777)

    for template, command_file in {
        "hpc": slurm_command_file_name,
        "parallel": manual_command_file_name,
    }.items():
        template_file = open(f"{template}.template.sh")
        content = template_file.read()
        template_file.close()

        content = content.format(num=str(number_of_task - 1), command_file=command_file)
        with open(f"{template}.sh", "w") as hpc_out_file:
            hpc_out_file.write(content)
        chmod(f"{template}.sh", 0o777)


if __name__ == "__main__":
    main()
