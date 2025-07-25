#!/usr/bin/env bash

usage() {
    echo "Usage: $0 [-n LINES] [--all|-a] [--level|-l LEVEL]"
    echo ""
    echo "Options:"
    echo "  -n LINES           Specify the number of lines to display from the end of the CSV file. Default is 10 for --level 1 and 30 for --level 2."
    echo "  --all, -a          Display all lines of the CSV file."
    echo "  --level, -l LEVEL  Specify the level of data to fetch: 1 for daily user data, 2 for detailed data. Default is 1."
    echo ""
    echo "Description:"
    echo "  This script runs a Python script using a specified Conda environment and then displays lines of a CSV file."
    echo ""
    echo "  The script runs either 'daily-user.py' (level 1) or 'details.py' (level 2) using the Conda environment named 'google-analytics'."
    echo "  It then determines the number of lines to display from the corresponding CSV file."
    echo "  If the '-n' option is provided, it uses the specified number of lines; if '--all' is provided, it shows all lines."
    echo "  Otherwise, it defaults to displaying 10 lines for level 1 and 30 lines for level 2."
    echo ""
    echo "  The script attempts to use the 'bat' or 'batcat' command for displaying the CSV file with syntax highlighting."
    echo "  If neither 'bat' nor 'batcat' is available, it falls back to using the 'cat' command."
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
    exit 1
fi

# conda bin
export PATH="$PATH:/opt/conda/bin"

# Default values
show_all=false
data_level=1
lines_to_show=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -n)
            lines_to_show="$2"
            shift 2
            ;;
        --all|-a)
            show_all=true
            shift
            ;;
        -l|--level)
            data_level="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Set default lines_to_show based on data_level if not specified
if [[ -z "$lines_to_show" ]]; then
    if [[ "$data_level" == 1 ]]; then
        lines_to_show=10    
    elif [[ "$data_level" == 2 ]]; then
        lines_to_show=30
    fi
fi

# Run the python script based on data type
script_dir="$(dirname "$0")"
mkdir -p "$script_dir/data"

if [[ "$data_level" == 1 ]]; then
    conda run --name google-analytics python "$script_dir/scripts/daily-user.py"
    csv_file="$script_dir/data/raw_data.csv"
elif [[ "$data_level" == 2 ]]; then
    conda run --name google-analytics python "$script_dir/scripts/details.py"
    csv_file="$script_dir/data/raw_data_detail.csv"
else
    echo "Invalid data level: $data_level. Must be 1 or 2."
    usage
    exit 1
fi

# Function to display the data
display_data() {
    if $show_all; then
        cat "$csv_file" | "$1" --style=plain --paging=never --language csv
    else
        {
            head -n 1 "$csv_file"
            tail -n "$lines_to_show" "$csv_file"
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
