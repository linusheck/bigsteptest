import sys

def generate_dtmc(n):
    constants = "\n".join([f"const double p{i};" for i in range(1, n)])
    final_transition = "\n        1-" + "-".join([f"p{i}" for i in range(1, n)]) + f" : (s'={n})"
    transitions_to_states = " +\n".join([f"        p{i} : (s'={i})" for i in range(1, n)]) + final_transition + ";"
    transitions_to_final = "\n".join([f"    [] s={i} -> 1/{i} : (s'={n+1}) + (1-1/{i}) : (s'={n+2});" for i in range(1, n+1)])

    return f"""
dtmc

{constants}

module nonsimple
    s : [0..{n+2}] init 0;
    
    [] s=0 ->
{transitions_to_states}
{transitions_to_final}
    
endmodule

label "target" = s={n+1};
"""

def generate_region(lower_bound, upper_bound, n):
    return ",".join([f"{lower_bound}<=p{i}<={upper_bound}" for i in range(1, n)])

if __name__ == "__main__":
    n = int(sys.argv[1])
    with open("nonsimple.pm", "w") as f:
        f.write(generate_dtmc(n))
    with open("region.txt", "w") as f:
        f.write(generate_region("1e-6", f"1/{n}", n))
    with open("region_not_gp.txt", "w") as f:
        f.write(generate_region("0", f"1/{n}", n))
    with open("region_not_gp_not_wd.txt", "w") as f:
        f.write(generate_region("0", f"2/{n}", n))
