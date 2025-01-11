#!/usr/bin/env bash

usage() {
    echo "Usage: $0 [-n LINES] [--all]"
    echo ""
    echo "Options:"
    echo "  -n LINES    Specify the number of lines to display from the end of the CSV file. Default is 10."
    echo "  --all       Display all lines of the CSV file."
    echo ""
    echo "Description:"
    echo "  This script runs a Python script using a specified Conda environment and then displays lines of a CSV file."
    echo ""
    echo "  The script first runs the 'analytics.py' Python script using the Conda environment named 'google-analytics'."
    echo "  It then determines the number of lines to display from the CSV file './data/raw_data.csv'."
    echo "  If the '-n' option is provided, it uses the specified number of lines; if '--all' is provided, it shows all lines."
    echo "  Otherwise, it defaults to displaying 10 lines."
    echo ""
    echo "  The script attempts to use the 'bat' or 'batcat' command for displaying the CSV file with syntax highlighting."
    echo "  If neither 'bat' nor 'batcat' is available, it falls back to using the 'cat' command."
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
    exit 1
fi

# Run the python script
script_dir="$(dirname "$0")"
mkdir -p "$script_dir/data"
conda run --name google-analytics python "$script_dir/daily-user.py"

# Determine the number of lines to show
lines_to_show=10
show_all=false
if [[ "$1" == "-n" ]]; then
    lines_to_show=$2
elif [[ "$1" == "--all" ]]; then
    show_all=true
fi

# Function to display the data
display_data() {
    if $show_all; then
        cat "$(dirname "$0")/data/raw_data.csv" | "$1" --style=plain --paging=never --language csv
    else
        {
            head -n 1 "$(dirname "$0")/data/raw_data.csv"
            tail -n "$lines_to_show" "$(dirname "$0")/data/raw_data.csv"
        } | "$1" --style=plain --paging=never --language csv
    fi
}

# Check for available command and display data
if command -v bat &> /dev/null; then
    display_data bat
elif command -v batcat &> /dev/null; then
    display_data batcat
else
    display_data cat
fi

