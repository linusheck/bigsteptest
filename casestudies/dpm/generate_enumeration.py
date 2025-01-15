import itertools

enumerate_params = ["P11", "P12", "P21", "P22", "P31", "P32", "P41", "P42", "P51", "P52", "P61", "P62", "P71", "P72", "P81", "P82"]
enumerate_values = [0, 1]
enumerate_regions = []

for values in itertools.product(enumerate_values, repeat=len(enumerate_params)):
    mapping = dict(zip(enumerate_params, values))
    enumerate_regions.append(mapping)

def to_constants(region):
    return ",".join([f"{key}={value}" for key, value in region.items()])

constants = [to_constants(region) for region in enumerate_regions]

commands = [f"../../../storm/build_release/bin/storm-pars --prism dpm.pm -prop \"R>=18.62914837 [F \\\"finished\\\"]\"  --mode partitioning --terminationCondition 0 '--regionverif:engine' robustpl '--minmax:method' vi -bisim --not-graph-preserving --region \"0.4<=startsend<=0.6,0.7<=contsend<=0.9\" -const {c} --noillustration" for c in constants]  

with open("dpm_enumeration.sh", "w") as f:
    f.write("\n".join(commands))
