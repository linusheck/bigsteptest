#!/usr/bin/env fish
set region (cat region_wd_not_gp.txt)
ulimit -v 32000000 && ../../../storm/build_release/bin/storm-pars --prism nonsimple.pm -prop "P>=0.51 [F \"target\"]" --mode partitioning --terminationCondition 0 '--regionverif:engine' robustpl '--minmax:method' vi -bisim --region $region --not-graph-preserving -v --timeout 6000
