#!/usr/bin/env fish

for i in (seq 2 32)
    python gen_nonsimple.py $i
    echo "New benchmark i=$i"
    echo
    echo "------------------------------"
    echo
    echo "Running on iMC (not-graph-preserving) with i=$i"
    ./imc_wd_not_gp.sh
    echo "------------------------------"
    echo
    echo "Running on iMC (not-graph-preserving and not-well-defined) with i=$i"
    ./imc_not_wd_not_gp.sh
end

for i in (seq 2 32)
    python gen_nonsimple.py $i
    echo "New benchmark i=$i"
    echo
    echo "------------------------------"
    echo "Running with graph-preserving region on MDP with i=$i"
    ./mdp_wd_gp.sh
    echo
    echo "------------------------------"
    echo "Running with graph-preserving region on iMC with i=$i"
    ./imc_wd_gp.sh
end
