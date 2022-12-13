#!/usr/bin/env bash

# PARAMETERS:

filename=./results/results;
text_output_filename=${filename}.txt;
csv_output_filename=${filename}.csv;


simulation_command=$@; # Uses program arguments as command

# Create and clean output files
touch $text_output_filename;
$NULL | tee $text_output_filename;
touch $csv_output_filename;
$NULL | tee $csv_output_filename;

# Run Simulator and redirect output to text file
$simulation_command >> $text_output_filename;