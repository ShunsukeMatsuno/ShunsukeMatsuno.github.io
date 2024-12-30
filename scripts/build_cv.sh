#!/bin/bash

# Define paths
TEX_SOURCE="assets/cv/cv.tex"
OUTPUT_DIR="static/cv"

# Ensure output directory exists
mkdir -p $OUTPUT_DIR

# Compile the TeX file using xelatex
xelatex -output-directory=$OUTPUT_DIR $TEX_SOURCE

# Cleanup intermediate files
find $OUTPUT_DIR -type f ! -name "cv.pdf" -delete
