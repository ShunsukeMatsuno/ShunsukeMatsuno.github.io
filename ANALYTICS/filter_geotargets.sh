#!/usr/bin/env bash

# Wrapper script to run Python geotargets filter in conda environment
script_dir="$(dirname "$0")"
cd "$script_dir"

# Check if argument provided, otherwise prompt for input
if [ $# -eq 0 ]; then
    echo -n "Enter the number to search for: "
    read search_string
else
    search_string="$1"
fi

# Run Python script with conda environment
bash -c "source ~/.bashrc; conda run --name google-analytics python filter_geotargets_core.py '$search_string'"