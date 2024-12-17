#!/usr/bin/env fish
set region (cat region.txt)
ulimit -v 32000000 && ../../../storm/build_release/bin/storm-pars --prism nonsimple.pm -prop "P>=0.01 [F \"target\"]" --mode verification --terminationCondition 0 '--regionverif:engine' pl '--minmax:method' vi -bisim --region $region -v --timeout 6000
