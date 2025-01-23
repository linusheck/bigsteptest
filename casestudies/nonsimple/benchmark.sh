#!/usr/bin/env fish

for i in (seq 2 32)
    python gen_nonsimple.py $i
    echo "==new run=="
    echo "Running on MDP with i=$i"
    echo
    echo "==new run=="
    ./test_mdp.sh
    python gen_nonsimple.py $i
    echo
    echo "==new run=="
    echo "Running on iMC with i=$i"
    ./test_imc.sh
    echo
    echo "==new run=="
    echo "Running on iMC (not-graph-preserving) with i=$i"
    ./test_imc_not_gp.sh
    echo
    echo "==new run=="
    echo "Running on iMC (not-graph-preserving and not-well-defined) with i=$i"
    ./test_imc_not_gp_not_wd.sh
end