#!/usr/bin/env bash

# PARAMETERS:

output_filename=results.txt;
simulation_command=$@; # Uses program arguments as command



# Create and clean output file
touch $output_filename;
$NULL | tee $output_filename;

# Run Simulator and redirect output to file
$simulation_command | tee -a $output_filename;