#!/usr/bin/env fish

for i in 32 64 128
    python gen_nonsimple.py $i
    echo "i=$i"
    echo
    echo "MDP"
    ./test_mdp.sh
    echo
    echo "iMC"
    ./test_imc.sh
    echo
    echo "iMC (full)"
    ./test_imc_fullregion.sh
end