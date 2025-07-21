#!/usr/bin/env bash

# Wrapper script to run Python geotargets filter in conda environment

show_usage() {
    echo "Usage: $(basename "$0") [search_string]"
    echo "Filter geotargets data by Criteria ID or Parent ID"
    echo ""
    echo "Arguments:"
    echo "  search_string    String to search for (optional, will prompt if not provided)"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $(basename "$0") 1023191"
    echo "  $(basename "$0")"
}

script_dir="$(dirname "$0")"
cd "$script_dir"

# Handle help flags
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

# Check if argument provided, otherwise prompt for input
if [ $# -eq 0 ]; then
    echo -n "Enter the number to search for: "
    read search_string
else
    search_string="$1"
fi

# Run Python script with conda environment
conda run --name google-analytics python filter-geotargets-core.py "$search_string"
