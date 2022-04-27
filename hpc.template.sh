#!/usr/bin/env zsh

### Project name. Required to actually use *our* cluster
#SBATCH -A moves

### Job name
#SBATCH --job-name=derivative

### Array job
#SBATCH --array=0-{num}

### Output file name. Zero-pad task id with 4
#SBATCH -o /home/%u/output/%x.%A_%4a.out

### Timelimit in hours:minutes:seconds
#SBATCH -t 2:00:00

### Number of available threads
#SBATCH --cpus-per-task=1

### Memory per thread in Megabytes. Total amount of available memory is --cpus-per-task * --mem-per-cpu
#SBATCH --mem-per-cpu=32G

### Receive all kinds of email notifications
#SBATCH --mail-type=ALL
#SBATCH --mail-user=linus.heck@rwth-aachen.de

### Load the module system configuration, necessary to load dependent libraries
source $HOME/hpc-scripts/prepareEnvironmentGcc.sh

### Change Directory to your working directory (binaries, etc)
cd $HOME/novatest/

./{command_file}
