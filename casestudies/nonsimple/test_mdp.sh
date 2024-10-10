region=`cat region.txt`
../../../storm/build_release/bin/storm-pars --prism nonsimple.pm -prop "P>=0.01 [F \"target\"]" --mode partitioning --terminationCondition 0 '--regionverif:engine' pl '--minmax:method' vi -bisim --region $region -v
