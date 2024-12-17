#!/usr/bin/env fish

for i in (seq 2 32)
    python gen_nonsimple.py $i
    echo "New benchmark i=$i"
    echo
    echo "------------------------------"
    echo "Running on MDP with i=$i"
    ./test_mdp.sh
    echo
    echo "------------------------------"
    echo "Running on iMC with i=$i"
    ./test_imc.sh
    echo
    echo "------------------------------"
    echo "Running on iMC (not-graph-preserving) with i=$i"
    ./test_imc_fullregion.sh
end