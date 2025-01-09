#!/usr/bin/env fish
set region (cat region_wd_gp.txt)
ulimit -v 32000000 && ../../../storm/build_release/bin/storm-pars --prism nonsimple.pm -prop "P>=0.501 [F \"target\"]" --mode partitioning --terminationCondition 0 '--regionverif:engine' pl '--minmax:method' vi -bisim --region $region -v --timeout 6000
