import glob
import subprocess
import argparse
from datetime import datetime
from os import path, makedirs, system, getcwd, chmod
import json
import sys
from pathlib import Path
import base64
import hashlib
import re

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

    if not gd_prop:
        prop += prop_dict["dir"]


    if not gd_prop and ("bound" not in prop_dict or prop_dict["bound"] is None):
        prop += "=?"
    else:
        if prop_dict["dir"] == "max":
            prop += ("<=" + str(-1) if gd_prop else ">=" + str(prop_dict["bound"]))
        if prop_dict["dir"] == "min":
            prop += (">=" + str(1e9) if gd_prop else "<=" + str(prop_dict["bound"]))

    label = prop_dict["label"]
    if label.startswith('"') or label.startswith("F"):
        prop += f" [{label}]"
    elif "=" in label:
        prop += f" [F {label}]"
    else:
        prop += f' [F "{label}"]'
    return prop.replace('"', '\\"')

def bool_to_cli_string(b):
    if b:
        return "true"
    else:
        return "false"

def get_model(invocation):
    for typ in ["pomdp", "prism", "jani", "drn"]:
        if typ in invocation:
            return invocation[typ]

def parse_jani_params(prism_file):
    content = Path(prism_file).read_text()
    return [x["name"] for x in json.loads(content)["constants"]]

def parse_prism_params(prism_file):
    content = Path(prism_file).read_text()
    result = re.findall(r"^const double (\w+);", content, re.MULTILINE)
    return result

def parse_drn_params(drn_file):
    content = Path(drn_file).read_text()
    lines = content.split("\n")
    parameters_line = None
    for i, line in enumerate(lines):
        if "@parameters" in line:
            parameters_line = lines[i + 1]
            break
    return [x for x in parameters_line.split(" ") if x]

def get_constants(invocation, params_file):
    model = get_model(invocation)
    if "prism" in invocation:
        return parse_prism_params(params_file)
    elif "drn" in invocation or "pomdp" in invocation:
        return parse_drn_params(params_file)
    elif "jani" in invocation:
        return parse_jani_params(params_file)
    raise RuntimeError("not supported invocation in combination with custom interval", invocation)

def get_region(invocation, params_file=None):
    if "region" in invocation:
        return f"--region \"{invocation['region']}\""
    elif "region_interval" in invocation:
        interval = invocation["region_interval"]
        if not params_file:
            return interval
        constants = get_constants(invocation, params_file)
        lower = interval.split(",")[0]
        upper = interval.split(",")[1]
        region = ",".join([f"{lower}<={c}<={upper}" for c in constants])
        return f"--region \"{region}\""
    elif "region_bound" in invocation:
        return f"--regionbound {invocation['region_bound']}"

def create_file_name(invocation: dict, constant_string: str, simple: bool) -> str:
    prop_dict = invocation["prop"]
    return (
        "_".join(
            [
                get_model(invocation).split(".")[0],
                prop_dict["type"],
                prop_dict["dir"],
                prop_dict["label"].replace(" ", "_").replace('"', "").replace("|", "").replace("(", "").replace(")", ""),
                prop_dict["reward_model"] if "reward_model" in prop_dict else "",
                prop_dict["use_robust_pla"] if "use_robust_pla" in prop_dict else "",
                prop_dict["splitting_strategy"] if "splitting_strategy" in prop_dict else "",
                prop_dict["estimate_method"] if "estimate_method" in prop_dict else "",
                "nonsimple" if not simple else "",
                constant_string,
                prop_dict["region_bound"] if "region_bound" in prop_dict else "",
                str(hashlib.sha256(get_region(invocation).encode()).hexdigest()),
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
    parser.add_argument(
        "--output", type=Path, default="/tmp/output", help="output folder"
    )
    parser.add_argument(
        "--jobs", type=int, default=8, help="number of parallel jobs"
    )
    parser.add_argument(
        "--timeout", type=int, default=600, help="job timeout"
    )
    parser.add_argument(
        "--drop-region-bound", type=bool, default=False, help="drop region bound in GD results"
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
            jani_file = None

            if "pomdp" in invocation:
                drn_file = (
                    Path(getcwd())
                    / ".build"
                    / folder
                    / (create_file_name(invocation, constant_string, invocation["simple"]) + ".drn")
                )
                storm_pomdp_command = (
                    "{binary} --parametric-drn {drn_file} --prism {pomdp} -prop \"{prop}\" -const '{constant_string}' "
                    + "--buildfull {simple} --exact --io:no-drn-placeholders --memorybound {memory_bound}"
                )
                storm_pomdp_command = storm_pomdp_command.format(
                    binary=args.storm_location / "storm-pomdp",
                    drn_file=drn_file,
                    constant_string=constant_string,
                    prop=prop,
                    pomdp=folder / invocation["pomdp"],
                    memory_bound=invocation["memory_bound"] if "memory_bound" in invocation else 1,
                    simple="--transformsimple --selfloopreduction" if invocation["simple"] else "",
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
                drn_file = getcwd() / folder / invocation["drn"]
            elif "jani" in invocation:
                jani_file = getcwd() / folder / invocation["jani"]
            else:
                print(invocation)
                print("neither a prism nor a drn file specified!")
                sys.exit(1)

            gd_result_file = (
                Path(getcwd())
                / ".build"
                / folder
                # GD should search the simple model, even if PLA model is the nonsimple variant
                / (create_file_name(invocation, constant_string, True) + ".gdresult")
            )

            print(invocation)

            if "override_bound" in invocation["prop"]:
                # override GD with manually found bound (we never do this)
                print(f"Overriding bound of {gd_result_file} with {invocation['prop']['bound']}")
                found_bound = invocation["prop"]["override_bound"]
            elif gd_result_file.exists():
                # cached GD
                found_bound = float(gd_result_file.read_text())
            else:
                # find a good bound with GD
                timeout = 30
                while True:
                    # GD should search the simple model, even if PLA model is the nonsimple variant
                    file = ("--explicit-drn " + str(drn_file).replace("nonsimple", "")
                        if drn_file
                        else "--prism " + str(prism_file)
                        if prism_file
                        else "--jani " + str(jani_file))
                    gd_command = '{binary} {file} {constants} -prop "{property}" --mode feasibility --feasibility:method gd {region} -bisim --timeout {timeout} --learning-rate 0.001 {additional_storm_args}'.format(
                        binary=(
                            Path(invocation["storm_location"]) / "storm-pars"
                            if "storm_location" in invocation
                            else args.storm_location / "storm-pars"
                        ),
                        file=file,
                        constants=(
                            ""
                            if (drn_file or not constant_string)
                            else "-const " + constant_string
                        ),
                        property=gd_prop,
                        timeout=timeout,
                        region=get_region(invocation, params_file=file.split(" ")[1]),
                        additional_storm_args=(
                            invocation["additional_storm_args"]
                            if "additional_storm_args" in invocation
                            else ""
                        ),
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
            
            if invocation["prop"]["type"] == "probability":
                if invocation["prop"]["dir"] == "min" and invocation["prop"]["bound"] >= 0.9999:
                    print("Probability bound is bigger than 0.9999, skipping")
                    continue
            if invocation["prop"]["dir"] == "max" and invocation["prop"]["bound"] <= 0.0001:
                print("Probability/reward bound is smaller than 0.0001, skipping")
                continue

            prop = create_prop_from_dict(invocation["prop"])
            print(prop)

            # run everything n times
            for i in range(args.times):
                use_robust_pla = (
                    "use_robust_pla" in invocation and invocation["use_robust_pla"]
                )

                file = ("--explicit-drn " + str(drn_file)
                    if drn_file
                    else "--prism " + str(prism_file)
                    if prism_file
                    else "--jani " + str(jani_file))

                command = '{binary} {file} {constants} -prop "{property}" {method} --mode partitioning {region} --terminationCondition 0 {robust_pla} -bisim {additional_storm_args} {splitting_strategy} {splitting_estimate} {splitting_threshold}'.format(
                    binary=(
                        Path(invocation["storm_location"]) / "storm-pars"
                        if "storm_location" in invocation
                        else args.storm_location / "storm-pars"
                    ),
                    file=file,
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
                    splitting_strategy=(
                        f"--splitting-heuristic {invocation['splitting_strategy']}"
                        if "splitting_strategy" in invocation
                        else ""
                    ),
                    splitting_estimate=(
                        f"--estimate-method {invocation['estimate_method']}"
                        if "estimate_method" in invocation
                        else ""
                    ),
                    splitting_threshold=(
                        f"--splitting-threshold {invocation['splitting_threshold']}"
                        if "splitting_threshold" in invocation
                        else ""
                    ),
                    region=get_region(invocation, params_file=file.split(" ")[1]),
                )

                json_str = json.dumps(invocation)
                echo_str = json_str.replace('\\"', "").replace('"', '\\"')

                manual_script += (
                    '( echo "'
                    + echo_str
                    + '"'
                    + f" && ulimit -v 128000000 && time timeout {args.timeout} "
                    + command
                    + "  ) > "
                    + str(args.output / "output"
                    / (create_file_name(invocation, constant_string, invocation["simple"])
                    + str(base64.b64encode(str(hash(json_str)).encode()))
                    + ".out")) +  " 2>&1"
                    + "\n"
                )

                number_of_task += 1

    (args.output / "output").mkdir()

    if args.dry_run:
        print(manual_script)
        sys.exit(0)

    manual_command_file_name = (
        args.output / "manual_commands.sh"
    )

    with open(manual_command_file_name, "w") as command_file:
        command_file.write(manual_script)

    chmod(manual_command_file_name, 0o777)

    content = "cat {command_file} | parallel --progress -j{jobs} bash -c {{}}"

    content = content.format(num=str(number_of_task - 1), command_file=manual_command_file_name, jobs=args.jobs)
    out_file_path = args.output / f"parallel.sh"
    with open(out_file_path, "w") as hpc_out_file:
        hpc_out_file.write(content)
    chmod(out_file_path, 0o777)


if __name__ == "__main__":
    main()
