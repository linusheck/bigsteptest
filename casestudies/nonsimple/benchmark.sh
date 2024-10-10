#!/usr/bin/env fish

for i in (seq 2 32)
    python gen_nonsimple.py $i
    echo "New benchmark i=$i"
    echo
    echo "------------------------------"
    echo "MDP $i"
    ./test_mdp.sh
    echo
    echo "------------------------------"
    echo "iMC $i"
    ./test_imc.sh
    echo
    echo "------------------------------"
    echo "iMC (full) $i"
    ./test_imc_fullregion.sh
end